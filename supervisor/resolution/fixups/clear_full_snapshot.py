"""Helpers to check and fix issues with free space."""
import logging
from typing import Optional

from ...const import SNAPSHOT_FULL
from ..const import MINIMUM_FULL_SNAPSHOTS, ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupClearFullSnapshot(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        full_snapshots = [
            x for x in self.sys_snapshots.list_snapshots if x.sys_type == SNAPSHOT_FULL
        ]

        if len(full_snapshots) < MINIMUM_FULL_SNAPSHOTS:
            return

        _LOGGER.info("Starting removal of old full snapshots")
        for snapshot in sorted(full_snapshots, key=lambda x: x.date)[:-1]:
            self.sys_snapshots.remove(snapshot)

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CLEAR_FULL_SNAPSHOT

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.FREE_SPACE
