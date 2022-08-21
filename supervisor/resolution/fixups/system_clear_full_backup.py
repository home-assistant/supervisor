"""Helpers to check and fix issues with free space."""
import logging

from ...backups.const import BackupType
from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemClearFullBackup(coresys)


class FixupSystemClearFullBackup(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not self.sys_backups.too_many_full_backups:
            return

        full_backups = [
            x for x in self.sys_backups.list_backups if x.sys_type == BackupType.FULL
        ]

        _LOGGER.info("Starting removal of old full backups")
        for backup in sorted(full_backups, key=lambda x: x.date)[
            : -1 * self.sys_backups.max_full_backups
        ]:
            self.sys_backups.remove(backup)

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CLEAR_FULL_BACKUP

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.FREE_SPACE]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return self.sys_backups.auto_backup
