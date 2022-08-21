"""Helpers to check and fix issues with free space."""
from ...const import CoreState
from ...coresys import CoreSys
from ..const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    MINIMUM_FULL_BACKUPS,
    ContextType,
    IssueType,
    SuggestionType,
)
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckFreeSpace(coresys)


class CheckFreeSpace(CheckBase):
    """Storage class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if self.sys_host.info.free_space > MINIMUM_FREE_SPACE_THRESHOLD:
            return

        suggestions: list[SuggestionType] = []
        if self.sys_backups.too_many_full_backups:
            suggestions.append(SuggestionType.CLEAR_FULL_BACKUP)
        elif self.sys_backups.max_full_backups > MINIMUM_FULL_BACKUPS:
            suggestions.append(SuggestionType.REDUCE_MAX_FULL_BACKUPS)

        self.sys_resolution.create_issue(
            IssueType.FREE_SPACE, ContextType.SYSTEM, suggestions=suggestions
        )

    async def approve_check(self, reference: str | None = None) -> bool:
        """Approve check if it is affected by issue."""
        if self.sys_host.info.free_space > MINIMUM_FREE_SPACE_THRESHOLD:
            return False
        return True

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
