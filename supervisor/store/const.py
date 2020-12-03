"""Constants for the add-on store."""
from enum import Enum


class StoreType(str, Enum):
    """Store Types."""

    CORE = "core"
    LOCAL = "local"
    GIT = "git"


class KnownGitError(str, Enum):
    """Known GIT error types."""

    BAD_REQUEST = "The requested URL returned error: 400"
