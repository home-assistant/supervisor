"""Helpers to check for detached addons."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckDetachedAddon(coresys)


class CheckDetachedAddon(CheckBase):
    """CheckDetachedAddon class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for addon in self.sys_addons.installed:
            if addon.is_detached:
                self.sys_resolution.create_issue(
                    IssueType.DETACHED_ADDON,
                    ContextType.ADDON,
                    reference=addon.slug,
                )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        return (
            addon := self.sys_addons.get(reference, local_only=True)
        ) and addon.is_detached

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.DETACHED_ADDON

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.SETUP]
