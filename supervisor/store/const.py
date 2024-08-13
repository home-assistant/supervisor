"""Constants for the add-on store."""

from enum import StrEnum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_HASSIO_STORE = Path(SUPERVISOR_DATA, "store.json")


class StoreType(StrEnum):
    """Store Types."""

    CORE = "core"
    LOCAL = "local"
    GIT = "git"
