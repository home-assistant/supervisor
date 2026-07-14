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
LANDINGPAGE_TYPE = "landingpage"
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

# Supervisor event versions offered to Core when the websocket connection is
# established. Core replies with the version it wants; a Core without support
# for the negotiation command gets DEFAULT_EVENT_VERSION. Version 1 sends job
# events with the legacy job names, version 2 with the new (app_*) names.
DEFAULT_EVENT_VERSION = 1
EVENT_VERSION_APP_JOB_NAMES = 2
SUPPORTED_EVENT_VERSIONS = frozenset(
    {DEFAULT_EVENT_VERSION, EVENT_VERSION_APP_JOB_NAMES}
)


class WSType(StrEnum):
    """Websocket types."""

    AUTH = "auth"
    SUPERVISOR_EVENT = "supervisor/event"
    SUPERVISOR_EVENT_VERSION = "supervisor/event_version"
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
