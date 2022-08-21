"""Helpers to check and fix issues with free space."""
import logging

from ...coresys import CoreSys
from ..const import ContextType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemCreateFullBackup(coresys)


class FixupSystemCreateFullBackup(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
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

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return self.sys_backups.auto_backup
