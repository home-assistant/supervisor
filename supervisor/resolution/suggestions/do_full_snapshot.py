"""Helpers to check and fix issues with free space."""
import logging

from .base import SuggestionBase
from ..const import ContextType, SuggestionType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SuggestionDoFullSnapshot(SuggestionBase):
    """Storage class for suggeston."""

    async def process_suggestion(self):
        """Initialize the suggestion class."""
        await self.sys_snapshots.do_snapshot_full()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a Suggestion enum."""
        return SuggestionType.CREATE_FULL_SNAPSHOT

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM
