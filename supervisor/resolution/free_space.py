"""Helpers to check and fix issues with free space."""
import logging

from ..const import SNAPSHOT_FULL
from ..coresys import CoreSys, CoreSysAttributes
from .const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    MINIMUM_FULL_SNAPSHOTS,
    ContextType,
    IssueType,
    SuggestionType,
)
from .type import Issue, Suggestion

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionStorage(CoreSysAttributes):
    """Storage class for resolution."""

    def __init__(self, coresys: CoreSys):
        """Initialize the storage class."""
        self.coresys = coresys

    def check_free_space(self) -> None:
        """Check free space."""
        if self.sys_host.info.free_space > MINIMUM_FREE_SPACE_THRESHOLD:
            return

        self.sys_resolution.issues = Issue(IssueType.FREE_SPACE, ContextType.SYSTEM)

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
            self.sys_resolution.suggestions = Suggestion(
                SuggestionType.CLEAR_FULL_SNAPSHOT, ContextType.SYSTEM
            )

        elif len(self.sys_snapshots.list_snapshots) == 0:
            # No snapshots, let's suggest the user to create one!
            self.sys_resolution.suggestions = Suggestion(
                SuggestionType.CREATE_FULL_SNAPSHOT, ContextType.SYSTEM
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
