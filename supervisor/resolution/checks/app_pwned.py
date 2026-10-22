"""Helpers to check core security."""

from datetime import timedelta
import logging

from ...const import ATTR_OPTIONS, AppState, CoreState
from ...coresys import CoreSys
from ...exceptions import PwnedConnectivityError, PwnedError, PwnedSecret
from ...jobs.const import JobCondition, JobThrottle
from ...jobs.decorator import Job
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckAppPwned(coresys)


class CheckAppPwned(CheckBase):
    """CheckAppPwned class for check."""

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return "app_pwned"

    @Job(
        name="check_app_pwned_run",
        conditions=[JobCondition.INTERNET_SYSTEM],
        throttle_period=timedelta(hours=24),
        throttle=JobThrottle.THROTTLE,
        internal=True,
    )
    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self.sys_security.pwned:
            _LOGGER.debug("Skipping %s, pwned is globally disabled", self.slug)
            return
        await self.sys_homeassistant.secrets.reload()

        for app in self.sys_apps.installed:
            try:
                options = await self._pwned_options(app.pwned)
            except PwnedConnectivityError:
                # Nudge a fresh connectivity check; the probe is
                # authoritative, this error path only hints that
                # something may be wrong.
                self.sys_supervisor.request_connectivity_check()
                return
            if not options:
                continue

            if app.state == AppState.STARTED:
                suggestions = [SuggestionType.EXECUTE_STOP]
            else:
                suggestions = None

            self.sys_resolution.create_issue(
                IssueType.PWNED,
                ContextType.ADDON,
                reference=app.slug,
                suggestions=suggestions,
                reference_extra={ATTR_OPTIONS: options},
            )

    async def _pwned_options(self, secrets: dict[str, str]) -> list[str]:
        """Return the option paths whose secret is pwned."""
        pwned_hashes: set[str] = set()
        for secret in set(secrets.values()):
            try:
                await self.sys_security.verify_secret(secret)
            except PwnedSecret:
                pwned_hashes.add(secret)
            except PwnedConnectivityError:
                raise
            except PwnedError:
                pass

        return sorted(
            path for path, secret in secrets.items() if secret in pwned_hashes
        )

    @Job(
        name="check_app_pwned_approve",
        conditions=[JobCondition.INTERNET_SYSTEM],
        internal=True,
    )
    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue."""
        if not issue.reference:
            return False

        # Uninstalled
        if not (app := self.sys_apps.get_local_only(issue.reference)):
            return False

        try:
            options = await self._pwned_options(app.pwned)
        except PwnedConnectivityError:
            # Cannot verify, keep the issue until the next check
            return True

        # Dismiss on any change so the check raises an issue listing the current options
        return bool(options) and issue.reference_extra == {ATTR_OPTIONS: options}

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
