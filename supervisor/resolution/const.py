"""Constants for the resoulution manager."""
from enum import Enum

SCHEDULED_HEALTHCHECK = 3600


class IssueType(str, Enum):
    """Issue type."""

    FREE_SPACE = "free_space"


class Suggestions(str, Enum):
    """Sugestion."""

    CLEAR_FULL_SNAPSHOT = "clear_full_snapshot"
    TAKE_FULL_SNAPSHOT = "take_full_snapshot"
