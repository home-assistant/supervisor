"""Add-on static data."""
from enum import Enum


class SnapshotAddonMode(str, Enum):
    """Snapshot mode of an Add-on."""

    HOT = "hot"
    COLD = "cold"


ATTR_SNAPSHOT = "snapshot"
