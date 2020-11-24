"""Helpers to check and fix issues with free space."""
import logging
from typing import List

from .base import CheckBase
from ...const import SNAPSHOT_FULL, CoreState
from ..const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    MINIMUM_FULL_SNAPSHOTS,
    ContextType,
    IssueType,
    SuggestionType,
)
from ..data import Suggestion

_LOGGER: logging.Logger = logging.getLogger(__name__)


class CheckFreeSpace(CheckBase):
    """Storage class for check."""

    async def run_test(self):
        """Run check."""
        if self.sys_host.info.free_space > MINIMUM_FREE_SPACE_THRESHOLD:
            if len(self.sys_snapshots.list_snapshots) == 0:
                # No snapshots, let's suggest the user to create one!
                self.sys_resolution.suggestions = Suggestion(
                    SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
                )
            return

        suggestions: List[SuggestionType] = []
        if (
            len(
                [
                    x
                    for x in self.sys_snapshots.list_snapshots
                    if x.sys_type == SNAPSHOT_FULL
                ]
            )
            >= MINIMUM_FULL_SNAPSHOTS
        ):
            suggestions.append(SuggestionType.CLEAR_FULL_SNAPSHOT)

        self.sys_resolution.create_issue(
            IssueType.FREE_SPACE, ContextType.SYSTEM, suggestions=suggestions
        )

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
        return [CoreState.RUNNING]
