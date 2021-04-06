"""Constants for the resoulution manager."""
from enum import Enum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_RESOLUTION = Path(SUPERVISOR_DATA, "resolution.json")

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
    APPARMOR = "apparmor"
    DOCKER_CONFIGURATION = "docker_configuration"
    DOCKER_VERSION = "docker_version"
    LXC = "lxc"
    NETWORK_MANAGER = "network_manager"
    OS = "os"
    PRIVILEGED = "privileged"
    SYSTEMD = "systemd"
    JOB_CONDITIONS = "job_conditions"
    CONTENT_TRUST = "content_trust"


class UnhealthyReason(str, Enum):
    """Reasons for unsupported status."""

    DOCKER = "docker"
    SUPERVISOR = "supervisor"
    SETUP = "setup"
    PRIVILEGED = "privileged"
    UNTRUSTED = "untrusted"


class IssueType(str, Enum):
    """Issue type."""

    FREE_SPACE = "free_space"
    DOCKER_RATELIMIT = "docker_ratelimit"
    CORRUPT_DOCKER = "corrupt_docker"
    CORRUPT_REPOSITORY = "corrupt_repository"
    SECURITY = "security"
    MISSING_IMAGE = "missing_image"
    UPDATE_FAILED = "update_failed"
    UPDATE_ROLLBACK = "update_rollback"
    FATAL_ERROR = "fatal_error"
    DNS_LOOP = "dns_loop"
    PWNED = "pwned"


class SuggestionType(str, Enum):
    """Sugestion type."""

    CLEAR_FULL_SNAPSHOT = "clear_full_snapshot"
    CREATE_FULL_SNAPSHOT = "create_full_snapshot"
    EXECUTE_UPDATE = "execute_update"
    EXECUTE_REPAIR = "execute_repair"
    EXECUTE_RESET = "execute_reset"
    EXECUTE_RELOAD = "execute_reload"
    EXECUTE_REMOVE = "execute_remove"
    EXECUTE_STOP = "execute_stop"
    REGISTRY_LOGIN = "registry_login"
