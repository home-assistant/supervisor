"""Helpers to check and fix issues with free space."""
import logging
from typing import Optional

from ..const import ContextType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupCreateFullBackup(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Creating a full backup")
        await self.sys_backups.do_backup_full()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CREATE_FULL_BACKUP

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM
