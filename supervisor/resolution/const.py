"""Constants for the resoulution manager."""
from enum import Enum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_RESOLUTION = Path(SUPERVISOR_DATA, "resolution.json")

SCHEDULED_HEALTHCHECK = 3600

MINIMUM_FREE_SPACE_THRESHOLD = 1
MINIMUM_FULL_BACKUPS = 2


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

    APPARMOR = "apparmor"
    CONTENT_TRUST = "content_trust"
    DBUS = "dbus"
    DOCKER_CONFIGURATION = "docker_configuration"
    DOCKER_VERSION = "docker_version"
    JOB_CONDITIONS = "job_conditions"
    LXC = "lxc"
    NETWORK_MANAGER = "network_manager"
    OS = "os"
    OS_AGENT = "os_agent"
    PRIVILEGED = "privileged"
    SOFTWARE = "software"
    SOURCE_MODS = "source_mods"
    SYSTEMD = "systemd"


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
    TRUST = "trust"


class SuggestionType(str, Enum):
    """Sugestion type."""

    CLEAR_FULL_BACKUP = "clear_full_backup"
    CREATE_FULL_BACKUP = "create_full_backup"
    EXECUTE_UPDATE = "execute_update"
    EXECUTE_REPAIR = "execute_repair"
    EXECUTE_RESET = "execute_reset"
    EXECUTE_RELOAD = "execute_reload"
    EXECUTE_REMOVE = "execute_remove"
    EXECUTE_STOP = "execute_stop"
    REGISTRY_LOGIN = "registry_login"
