"""Helpers to check and fix issues with free space."""
import logging
from typing import Optional

from ...backups.const import BackupType
from ..const import MINIMUM_FULL_BACKUPS, ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupClearFullBackup(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        full_backups = [
            x for x in self.sys_backups.list_backups if x.sys_type == BackupType.FULL
        ]

        if len(full_backups) < MINIMUM_FULL_BACKUPS:
            return

        _LOGGER.info("Starting removal of old full backups")
        for backup in sorted(full_backups, key=lambda x: x.date)[:-1]:
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
