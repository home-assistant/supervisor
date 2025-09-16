"""Helpers to check and fix issues with free space."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import MINIMUM_FREE_SPACE_THRESHOLD, ContextType, IssueType
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckFreeSpace(coresys)


class CheckFreeSpace(CheckBase):
    """Storage class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if await self.approve_check():
            self.sys_resolution.create_issue(IssueType.FREE_SPACE, ContextType.SYSTEM)

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        return await self.sys_host.info.free_space() <= MINIMUM_FREE_SPACE_THRESHOLD

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.FREE_SPACE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
