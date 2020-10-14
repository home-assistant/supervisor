"""Constants for the resoulution manager."""
from enum import Enum

SCHEDULED_HEALTHCHECK = 3600

MINIMUM_FREE_SPACE_THRESHOLD = 1
MINIMUM_FULL_SNAPSHOTS = 2


class UnsupportedReason(str, Enum):
    """Reasons for unsupported status."""

    CONTAINER = "container"
    DBUS = "dbus"
    DOCKER_CONFIGURATION = "docker_configuration"
    DOCKER_VERSION = "docker_version"
    LXC = "lxc"
    NETWORK_MANAGER = "network_manager"
    OS = "os"
    PRIVILEGED = "privileged"
    SYSTEMD = "systemd"


class IssueType(str, Enum):
    """Issue type."""

    FREE_SPACE = "free_space"


class Suggestions(str, Enum):
    """Sugestion."""

    CLEAR_FULL_SNAPSHOT = "clear_full_snapshot"
    CREATE_SNAPSHOT = "create_snapshot"
