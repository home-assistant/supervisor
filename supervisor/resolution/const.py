"""Constants for the resoulution manager."""
from enum import Enum

SCHEDULED_HEALTHCHECK = 3600

MINIMUM_FREE_SPACE_THRESHOLD = 1
MINIMUM_FULL_SNAPSHOTS = 2


class ContextType(str, Enum):
    """Place where somethings was happening."""

    ADDON = "addon"
    CORE = "core"
    OS = "os"
    PLUGIN = "plugin"
    SUPERVISOR = "supervisor"
    STORE = "store"
    SYSTEM = "system"


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


class UnhealthyReason(str, Enum):
    """Reasons for unsupported status."""

    DOCKER = "docker"
    SUPERVISOR = "supervisor"
    SETUP = "setup"
    PRIVILEGED = "privileged"


class IssueType(str, Enum):
    """Issue type."""

    FREE_SPACE = "free_space"
    CORRUPT_DOCKER = "corrupt_docker"
    CORRUPT_REPOSITORY = "corrupt_repository"
    MISSING_IMAGE = "missing_image"
    UPDATE_FAILED = "update_failed"
    UPDATE_ROLLBACK = "update_rollback"
    FATAL_ERROR = "fatal_error"
    DNS_LOOP = "dns_loop"


class SuggestionType(str, Enum):
    """Sugestion type."""

    CLEAR_FULL_SNAPSHOT = "clear_full_snapshot"
    CREATE_FULL_SNAPSHOT = "create_full_snapshot"
    EXECUTE_UPDATE = "execute_update"
    EXECUTE_REPAIR = "execute_repair"
    EXECUTE_RESET = "execute_reset"
    EXECUTE_RELOAD = "execute_reload"
    NEW_INITIALIZE = "new_initialize"
