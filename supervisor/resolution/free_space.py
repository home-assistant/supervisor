"""Helpers to check and fix issues with free space."""
import logging

from ..coresys import CoreSys
from .const import IssueType, Suggestions

_LOGGER: logging.Logger = logging.getLogger(__name__)


def check_free_space(coresys: CoreSys):
    """Check free space."""
    if coresys.host.info.free_space > 1:
        return

    coresys.resolution.issues = IssueType.FREE_SPACE

    if len([x for x in coresys.snapshots.list_snapshots if x.sys_type == "full"]) >= 2:
        coresys.resolution.suggestions = Suggestions.CLEAR_FULL_SNAPSHOT


def clean_full_snapshots(coresys: CoreSys):
    """Clean out old snapshots."""
    full_snapshots = [
        x for x in coresys.snapshots.list_snapshots if x.sys_type == "full"
    ]

    if len(full_snapshots) < 2:
        return

    _LOGGER.info("Starting removal of old full snapshots")
    for snapshot in full_snapshots.sort(key=lambda x: x.date, reverse=True)[:-1]:
        coresys.snapshots.remove(snapshot)
