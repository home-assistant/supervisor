"""Helpers to check for app port conflicts."""

from ...const import AppState, CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType
from ..data import Issue
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckAppPortConflictCore(coresys)


class CheckAppPortConflictCore(CheckBase):
    """CheckAppPortConflictCore class for check."""

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return "app_port_conflict_core"

    async def run_check(self) -> None:
        """Skip check if not affected by issue.

        This situation is detected when core reports in on startup. This check
        is only used to approve or dismiss existing issues rather then make new ones.
        """

    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue."""
        if (
            not issue.reference
            or not issue.reference_extra
            or not (conflict_port := issue.reference_extra.get("port"))
        ):
            return False

        # Home Assistant changed ports
        if self.sys_homeassistant.api_port != conflict_port:
            return False

        # Uninstalled
        if not (app := self.sys_apps.get_local_only(issue.reference)):
            return False

        # If the app and Home Assistant are running then the conflict has been resolved
        if (
            app.state in (AppState.STARTED, AppState.STARTUP)
            and await self.sys_homeassistant.api.check_api_state()
        ):
            return False

        # Our validation option are not totally reliable. So we assume if the port
        # is still listed its still a problem. Or if the app runs on host network
        # and can expose ports without listing them.
        # If we're wrong, user can dismiss it. Or just start the app and HA
        ports = app.ports or {}
        return app.host_network or conflict_port in ports.values()

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.APP_PORT_CONFLICT_CORE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
