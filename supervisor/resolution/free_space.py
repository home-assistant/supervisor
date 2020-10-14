"""Helpers to check and fix issues with free space."""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from .const import (
    MINIMUM_FREE_SPACE_THRESHOLD,
    MINIMUM_FULL_SNAPSHOTS,
    IssueType,
    Suggestions,
)

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

        self.sys_resolution.issues = IssueType.FREE_SPACE

        if (
            len([x for x in self.sys_snapshots.list_snapshots if x.sys_type == "full"])
            >= MINIMUM_FULL_SNAPSHOTS
        ):
            self.sys_resolution.suggestions = Suggestions.CLEAR_FULL_SNAPSHOT

    def clean_full_snapshots(self):
        """Clean out old snapshots."""
        full_snapshots = [
            x for x in self.sys_snapshots.list_snapshots if x.sys_type == "full"
        ]

        if len(full_snapshots) < MINIMUM_FULL_SNAPSHOTS:
            return

        _LOGGER.info("Starting removal of old full snapshots")
        for snapshot in full_snapshots.sort(key=lambda x: x.date, reverse=True)[:-1]:
            self.sys_snapshots.remove(snapshot)
