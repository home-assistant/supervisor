"""Constants for the resoulution manager."""
from enum import Enum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_RESOLUTION = Path(SUPERVISOR_DATA, "resolution.json")

SCHEDULED_HEALTHCHECK = 3600

MINIMUM_FREE_SPACE_THRESHOLD = 1
MINIMUM_FULL_BACKUPS = 2

DNS_CHECK_HOST = "_checkdns.home-assistant.io"
DNS_ERROR_NO_DATA = 1


class ContextType(str, Enum):
    """Place where somethings was happening."""

    ADDON = "addon"
    CORE = "core"
    DNS_SERVER = "dns_server"
    OS = "os"
    PLUGIN = "plugin"
    SUPERVISOR = "supervisor"
    STORE = "store"
    SYSTEM = "system"


class UnsupportedReason(str, Enum):
    """Reasons for unsupported status."""

    APPARMOR = "apparmor"
    CGROUP_VERSION = "cgroup_version"
    CONNECTIVITY_CHECK = "connectivity_check"
    CONTENT_TRUST = "content_trust"
    DBUS = "dbus"
    DNS_SERVER = "dns_server"
    DOCKER_CONFIGURATION = "docker_configuration"
    DOCKER_VERSION = "docker_version"
    JOB_CONDITIONS = "job_conditions"
    LXC = "lxc"
    NETWORK_MANAGER = "network_manager"
    OS = "os"
    OS_AGENT = "os_agent"
    PRIVILEGED = "privileged"
    RESTART_POLICY = "restart_policy"
    SOFTWARE = "software"
    SOURCE_MODS = "source_mods"
    SUPERVISOR_VERSION = "supervisor_version"
    SYSTEMD = "systemd"
    SYSTEMD_JOURNAL = "systemd_journal"
    SYSTEMD_RESOLVED = "systemd_resolved"


class UnhealthyReason(str, Enum):
    """Reasons for unsupported status."""

    DOCKER = "docker"
    SUPERVISOR = "supervisor"
    SETUP = "setup"
    PRIVILEGED = "privileged"
    UNTRUSTED = "untrusted"


class IssueType(str, Enum):
    """Issue type."""

    CORRUPT_DOCKER = "corrupt_docker"
    CORRUPT_REPOSITORY = "corrupt_repository"
    CORRUPT_FILESYSTEM = "corrupt_filesystem"
    DNS_LOOP = "dns_loop"
    DNS_SERVER_FAILED = "dns_server_failed"
    DNS_SERVER_IPV6_ERROR = "dns_server_ipv6_error"
    DOCKER_RATELIMIT = "docker_ratelimit"
    FATAL_ERROR = "fatal_error"
    FREE_SPACE = "free_space"
    IPV4_CONNECTION_PROBLEM = "ipv4_connection_problem"
    MISSING_IMAGE = "missing_image"
    NO_CURRENT_BACKUP = "no_current_backup"
    PWNED = "pwned"
    REBOOT_REQUIRED = "reboot_required"
    SECURITY = "security"
    TRUST = "trust"
    UPDATE_FAILED = "update_failed"
    UPDATE_ROLLBACK = "update_rollback"


class SuggestionType(str, Enum):
    """Sugestion type."""

    CLEAR_FULL_BACKUP = "clear_full_backup"
    CREATE_FULL_BACKUP = "create_full_backup"
    EXECUTE_INTEGRITY = "execute_integrity"
    EXECUTE_REBOOT = "execute_reboot"
    EXECUTE_RELOAD = "execute_reload"
    EXECUTE_REMOVE = "execute_remove"
    EXECUTE_REPAIR = "execute_repair"
    EXECUTE_RESET = "execute_reset"
    EXECUTE_STOP = "execute_stop"
    EXECUTE_UPDATE = "execute_update"
    REGISTRY_LOGIN = "registry_login"
