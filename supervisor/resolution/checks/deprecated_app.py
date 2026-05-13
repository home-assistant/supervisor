"""Helpers to check for deprecated apps."""

from ...const import AppStage, CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDeprecatedApp(coresys)


class CheckDeprecatedApp(CheckBase):
    """CheckDeprecatedApp class for check."""

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return "deprecated_addon"

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for app in self.sys_apps.installed:
            if app.stage == AppStage.DEPRECATED:
                self.sys_resolution.create_issue(
                    IssueType.DEPRECATED_ADDON,
                    ContextType.ADDON,
                    reference=app.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        app = self.sys_apps.get_local_only(reference)
        return app is not None and app.stage == AppStage.DEPRECATED

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DEPRECATED_ADDON

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP]
