"""Helpers to check and fix issues with free space."""
import logging

from .base import FixupBase
from ..const import ContextType, SuggestionType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupDoFullSnapshot(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self):
        """Initialize the fixup class."""
        await self.sys_snapshots.do_snapshot_full()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CREATE_FULL_SNAPSHOT

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM
