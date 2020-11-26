"""Helpers to check and fix issues with free space."""
import logging
from typing import List

from ..const import SNAPSHOT_FULL
from ..coresys import CoreSys, CoreSysAttributes
from .const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    MINIMUM_FULL_SNAPSHOTS,
    ContextType,
    IssueType,
    SuggestionType,
)
from .data import Suggestion

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionStorage(CoreSysAttributes):
    """Storage class for resolution."""

    def __init__(self, coresys: CoreSys):
        """Initialize the storage class."""
        self.coresys = coresys

    def check_free_space(self) -> None:
        """Check free space."""
        free_space = self.sys_host.info.free_space
        if free_space > MINIMUM_FREE_SPACE_THRESHOLD:
            if len(self.sys_snapshots.list_snapshots) == 0:
                # No snapshots, let's suggest the user to create one!
                self.sys_resolution.suggestions = Suggestion(
                    SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
                )
            return

        _LOGGER.warning("Free space left on the device: %sGB", free_space)

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
            IssueType.FREE_SPACE,
            ContextType.SYSTEM,
            suggestions=suggestions,
            reference=str(free_space),
        )

    def clean_full_snapshots(self):
        """Clean out all old full snapshots, but keep the most recent."""
        full_snapshots = [
            x for x in self.sys_snapshots.list_snapshots if x.sys_type == SNAPSHOT_FULL
        ]

        if len(full_snapshots) < MINIMUM_FULL_SNAPSHOTS:
            return

        _LOGGER.info("Starting removal of old full snapshots")
        for snapshot in sorted(full_snapshots, key=lambda x: x.date)[:-1]:
            self.sys_snapshots.remove(snapshot)
