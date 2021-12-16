"""Constants for homeassistant."""
from enum import Enum

from awesomeversion import AwesomeVersion

from ..const import CoreState

LANDINGPAGE: AwesomeVersion = AwesomeVersion("landingpage")

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


MIN_VERSION = {
    WSType.SUPERVISOR_EVENT: "2021.2.4",
    WSType.BACKUP_START: "2021.12.0",
    WSType.BACKUP_END: "2021.12.0",
}


class WSEvent(str, Enum):
    """Websocket events."""

    ADDON = "addon"
    SUPERVISOR_UPDATE = "supervisor_update"
