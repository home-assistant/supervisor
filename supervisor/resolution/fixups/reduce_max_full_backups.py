"""Helpers to check and fix issues with free space."""
from ...coresys import CoreSys
from ..const import MINIMUM_FULL_BACKUPS, ContextType, IssueType, SuggestionType
from .base import FixupBase
from .system_clear_full_backup import FixupSystemClearFullBackup


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupReduceMaxFullBackups(coresys)


class FixupReduceMaxFullBackups(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if self.sys_backups.max_full_backups <= MINIMUM_FULL_BACKUPS:
            return

        self.sys_backups.max_full_backups = MINIMUM_FULL_BACKUPS

        await FixupSystemClearFullBackup(self.coresys).process_fixup()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.REDUCE_MAX_FULL_BACKUPS

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.FREE_SPACE]
