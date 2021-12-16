"""Constants for homeassistant."""
from enum import Enum

from awesomeversion import AwesomeVersion

from ..const import CoreState

LANDINGPAGE: AwesomeVersion = AwesomeVersion("landingpage")

MIN_VERSION = {
    "supervisor/event": "2021.2.4",
    "backup/start": "2021.12.0",
    "backup/end": "2021.12.0",
}

CLOSING_STATES = [
    CoreState.SHUTDOWN,
    CoreState.STOPPING,
    CoreState.CLOSE,
]


class WSType(str, Enum):
    """Websocket types."""

    AUTH = "auth"
    SUPERVISOR_EVENT = "supervisor/event"
    BACKUP_START = "backup/start"
    BACKUP_END = "backup/start"


class WSEvent(str, Enum):
    """Websocket events."""

    ADDON = "addon"
    SUPERVISOR_UPDATE = "supervisor_update"
