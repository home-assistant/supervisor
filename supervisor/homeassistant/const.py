"""Constants for homeassistant."""

from datetime import timedelta
from enum import StrEnum
from pathlib import PurePath

from awesomeversion import AwesomeVersion

from ..const import CoreState

ATTR_ERROR = "error"
ATTR_OVERRIDE_IMAGE = "override_image"
ATTR_SUCCESS = "success"
LANDINGPAGE: AwesomeVersion = AwesomeVersion("landingpage")
WATCHDOG_RETRY_SECONDS = 10
WATCHDOG_MAX_ATTEMPTS = 5
WATCHDOG_THROTTLE_PERIOD = timedelta(minutes=30)
WATCHDOG_THROTTLE_MAX_CALLS = 10
SAFE_MODE_FILENAME = PurePath("safe-mode")

CLOSING_STATES = [
    CoreState.SHUTDOWN,
    CoreState.STOPPING,
    CoreState.CLOSE,
]


class WSType(StrEnum):
    """Websocket types."""

    AUTH = "auth"
    SUPERVISOR_EVENT = "supervisor/event"
    BACKUP_START = "backup/start"
    BACKUP_END = "backup/end"
    HASSIO_UPDATE_ADDON = "hassio/update/addon"


class WSEvent(StrEnum):
    """Websocket events."""

    ADDON = "addon"
    HEALTH_CHANGED = "health_changed"
    ISSUE_CHANGED = "issue_changed"
    ISSUE_REMOVED = "issue_removed"
    JOB = "job"
    SUPERVISOR_UPDATE = "supervisor_update"
    SUPPORTED_CHANGED = "supported_changed"
