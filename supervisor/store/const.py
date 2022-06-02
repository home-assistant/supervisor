"""Constants for the add-on store."""
from enum import Enum
from pathlib import Path

from supervisor.const import SUPERVISOR_DATA

FILE_HASSIO_STORE = Path(SUPERVISOR_DATA, "store.json")


class StoreType(str, Enum):
    """Store Types."""

    CORE = "core"
    LOCAL = "local"
    GIT = "git"
