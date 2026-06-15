"""Helpers to check for detached apps due to removal from repo."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDetachedAppRemoved(coresys)


class CheckDetachedAppRemoved(CheckBase):
    """CheckDetachedAppRemoved class for check."""

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return "detached_addon_removed"

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for app in self.sys_apps.installed:
            if app.is_detached and app.repository in self.sys_store.repositories:
                self.sys_resolution.create_issue(
                    IssueType.DETACHED_ADDON_REMOVED,
                    ContextType.ADDON,
                    reference=app.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
                )

    async def approve_check(self, issue: Issue) -> bool:
        """Approve check if it is affected by issue."""
        if not issue.reference:
            return False

        app = self.sys_apps.get_local_only(issue.reference)
        return app is not None and app.is_detached

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DETACHED_ADDON_REMOVED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP]
