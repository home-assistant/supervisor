"""Helpers to check for deprecated addons."""

from ...const import AddonStage, CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDeprecatedAddon(coresys)


class CheckDeprecatedAddon(CheckBase):
    """CheckDeprecatedAddon class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for addon in self.sys_addons.installed:
            if addon.stage == AddonStage.DEPRECATED:
                self.sys_resolution.create_issue(
                    IssueType.DEPRECATED_ADDON,
                    ContextType.ADDON,
                    reference=addon.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        addon = self.sys_addons.get_local_only(reference)
        return addon is not None and addon.stage == AddonStage.DEPRECATED

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
