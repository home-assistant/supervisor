"""Helpers to check for add-ons with deprecated architectures."""

from ...const import AddonStage, CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDeprecatedArchAddon(coresys)


class CheckDeprecatedArchAddon(CheckBase):
    """CheckDeprecatedArchAddon class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for addon in self.sys_addons.installed:
            if addon.stage == AddonStage.DEPRECATED:
                continue

            if addon.has_deprecated_arch and not addon.has_supported_arch:
                self.sys_resolution.create_issue(
                    IssueType.DEPRECATED_ARCH_ADDON,
                    ContextType.ADDON,
                    reference=addon.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if not reference:
            return False

        addon = self.sys_addons.get_local_only(reference)
        return (
            addon is not None
            and addon.stage != AddonStage.DEPRECATED
            and addon.has_deprecated_arch
            and not addon.has_supported_arch
        )

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DEPRECATED_ARCH_ADDON

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.SETUP, CoreState.RUNNING]
