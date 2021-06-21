"""Helpers to check and fix issues with free space."""
from typing import List, Optional

from ...const import BACKUP_FULL, CoreState
from ...coresys import CoreSys
from ..const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    MINIMUM_FULL_BACKUPS,
    ContextType,
    IssueType,
    SuggestionType,
)
from ..data import Suggestion
from .base import CheckBase


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckFreeSpace(coresys)


class CheckFreeSpace(CheckBase):
    """Storage class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if self.sys_host.info.free_space > MINIMUM_FREE_SPACE_THRESHOLD:
            if len(self.sys_backups.list_backups) == 0:
                # No backups, let's suggest the user to create one!
                self.sys_resolution.suggestions = Suggestion(
                    SuggestionType.CREATE_FULL_BACKUP, ContextType.SYSTEM
                )
            return

        suggestions: List[SuggestionType] = []
        if (
            len([x for x in self.sys_backups.list_backups if x.sys_type == BACKUP_FULL])
            >= MINIMUM_FULL_BACKUPS
        ):
            suggestions.append(SuggestionType.CLEAR_FULL_BACKUP)

        self.sys_resolution.create_issue(
            IssueType.FREE_SPACE, ContextType.SYSTEM, suggestions=suggestions
        )

    async def approve_check(self, reference: Optional[str] = None) -> bool:
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
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING, CoreState.STARTUP]
