"""Helpers to check for apps still calling Supervisor over TCP."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType
from ..data import Issue
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDeprecatedTcpApiApp(coresys)


class CheckDeprecatedTcpApiApp(CheckBase):
    """CheckDeprecatedTcpApiApp class for check."""

    async def run_check(self) -> None:
        """Skip check if not affected by issue.

        The security middleware raises this issue when it sees an app's token
        used over TCP. This check is only used to approve or dismiss existing
        issues rather than make new ones.
        """

    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue."""
        if (
            not issue.reference
            or not issue.reference_extra
            or not (version := issue.reference_extra.get("version"))
        ):
            return False

        # Uninstalled
        if not (app := self.sys_apps.get_local_only(issue.reference)):
            return False

        # An update may have moved it to the socket, the next TCP request raises
        # the issue again. Without TCP access the app has no token to call it with.
        # The update channel can change while running.
        return (
            str(app.version) == version
            and app.supervisor_api_tcp
            and app.user_is_developer
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DEPRECATED_TCP_API_REQUEST

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
