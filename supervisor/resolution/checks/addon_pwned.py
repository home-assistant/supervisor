"""Helpers to check core security."""
from datetime import timedelta
import logging

from ...const import AddonState, CoreState
from ...coresys import CoreSys
from ...exceptions import PwnedConnectivityError, PwnedError, PwnedSecret
from ...jobs.const import JobCondition, JobExecutionLimit
from ...jobs.decorator import Job
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckAddonPwned(coresys)


class CheckAddonPwned(CheckBase):
    """CheckAddonPwned class for check."""

    @Job(
        name="check_addon_pwned_run",
        conditions=[JobCondition.INTERNET_SYSTEM],
        limit=JobExecutionLimit.THROTTLE,
        throttle_period=timedelta(hours=24),
    )
    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self.sys_security.pwned:
            _LOGGER.warning("Skipping %s, pwned is globally disabled", self.slug)
            return
        await self.sys_homeassistant.secrets.reload()

        for addon in self.sys_addons.installed:
            secrets = addon.pwned
            if not secrets:
                continue

            # check passwords
            for secret in secrets:
                try:
                    await self.sys_security.verify_secret(secret)
                except PwnedConnectivityError:
                    self.sys_supervisor.connectivity = False
                    return
                except PwnedSecret:
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
                except PwnedError:
                    pass

    @Job(name="check_addon_pwned_approve", conditions=[JobCondition.INTERNET_SYSTEM])
    async def approve_check(self, reference: str | None = None) -> bool:
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
            try:
                await self.sys_security.verify_secret(secret)
            except PwnedSecret:
                return True
            except PwnedError:
                pass

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
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
