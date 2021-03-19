"""Helpers to check core security."""
from contextlib import suppress
from datetime import timedelta
from typing import List, Optional

from ...const import AddonState, CoreState
from ...coresys import CoreSys
from ...exceptions import PwnedConnectivityError, PwnedError
from ...jobs.const import JobCondition, JobExecutionLimit
from ...jobs.decorator import Job
from ...utils.pwned import check_pwned_password
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckAddonPwned(coresys)


class CheckAddonPwned(CheckBase):
    """CheckAddonPwned class for check."""

    @Job(
        conditions=[JobCondition.INTERNET_SYSTEM],
        limit=JobExecutionLimit.THROTTLE,
        throttle_period=timedelta(hours=24),
    )
    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        await self.sys_homeassistant.secrets.reload()

        for addon in self.sys_addons.installed:
            secrets = addon.pwned
            if not secrets:
                continue

            # check passwords
            for secret in secrets:
                try:
                    if not await check_pwned_password(self.sys_websession, secret):
                        continue
                except PwnedConnectivityError:
                    self.sys_supervisor.connectivity = False
                    return
                except PwnedError:
                    continue

                # Check possible suggestion
                if addon.state == AddonState.STARTED:
                    suggestions = [SuggestionType.EXECUTE_STOP]
                else:
                    suggestions = None

                self.sys_resolution.create_issue(
                    IssueType.PWNED,
                    ContextType.ADDON,
                    reference=addon.slug,
                    suggestions=suggestions,
                )
                break

    @Job(conditions=[JobCondition.INTERNET_SYSTEM])
    async def approve_check(self, reference: Optional[str] = None) -> bool:
        """Approve check if it is affected by issue."""
        addon = self.sys_addons.get(reference)

        # Uninstalled
        if not addon or not addon.is_installed:
            return False

        # Not in use anymore
        secrets = addon.pwned
        if not secrets:
            return False

        # Check if still pwned
        for secret in secrets:
            with suppress(PwnedError):
                if not await check_pwned_password(self.sys_websession, secret):
                    continue
            return True

        return False

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.PWNED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
