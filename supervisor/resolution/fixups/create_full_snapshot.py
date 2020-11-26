"""Helpers to check and fix issues with free space."""
import logging

from ..const import ContextType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupCreateFullSnapshot(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Create a full snapshot as backup")
        await self.sys_snapshots.do_snapshot_full()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CREATE_FULL_SNAPSHOT

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM
