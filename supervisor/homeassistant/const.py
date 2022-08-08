"""Constants for homeassistant."""
from datetime import timedelta
from enum import Enum

from awesomeversion import AwesomeVersion

from ..const import CoreState

LANDINGPAGE: AwesomeVersion = AwesomeVersion("landingpage")
WATCHDOG_RETRY_SECONDS = 10
WATCHDOG_MAX_ATTEMPTS = 5
WATCHDOG_THROTTLE_PERIOD = timedelta(minutes=30)
WATCHDOG_THROTTLE_MAX_CALLS = 10

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
    BACKUP_END = "backup/end"


class WSEvent(str, Enum):
    """Websocket events."""

    ADDON = "addon"
    SUPERVISOR_UPDATE = "supervisor_update"
