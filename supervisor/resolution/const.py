"""Constants for the resoulution manager."""

from enum import StrEnum
from pathlib import Path

from ..const import SUPERVISOR_DATA

FILE_CONFIG_RESOLUTION = Path(SUPERVISOR_DATA, "resolution.json")

SCHEDULED_HEALTHCHECK = 3600

MINIMUM_FREE_SPACE_THRESHOLD = 1
MINIMUM_FULL_BACKUPS = 2

DNS_CHECK_HOST = "_checkdns.home-assistant.io"
DNS_ERROR_NO_DATA = 1

CGROUP_V1_VERSION = "1"
CGROUP_V2_VERSION = "2"


class ContextType(StrEnum):
    """Place where somethings was happening."""

    ADDON = "addon"
    CORE = "core"
    DNS_SERVER = "dns_server"
    MOUNT = "mount"
    OS = "os"
    PLUGIN = "plugin"
    SUPERVISOR = "supervisor"
    STORE = "store"
    SYSTEM = "system"


class UnsupportedReason(StrEnum):
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
    VIRTUALIZATION_IMAGE = "virtualization_image"


class UnhealthyReason(StrEnum):
    """Reasons for unsupported status."""

    DOCKER = "docker"
    OSERROR_BAD_MESSAGE = "oserror_bad_message"
    PRIVILEGED = "privileged"
    SUPERVISOR = "supervisor"
    SETUP = "setup"
    UNTRUSTED = "untrusted"


class IssueType(StrEnum):
    """Issue type."""

    BOOT_FAIL = "boot_fail"
    CORRUPT_DOCKER = "corrupt_docker"
    CORRUPT_REPOSITORY = "corrupt_repository"
    CORRUPT_FILESYSTEM = "corrupt_filesystem"
    DETACHED_ADDON_MISSING = "detached_addon_missing"
    DETACHED_ADDON_REMOVED = "detached_addon_removed"
    DEVICE_ACCESS_MISSING = "device_access_missing"
    DISABLED_DATA_DISK = "disabled_data_disk"
    DNS_LOOP = "dns_loop"
    DNS_SERVER_FAILED = "dns_server_failed"
    DNS_SERVER_IPV6_ERROR = "dns_server_ipv6_error"
    DOCKER_CONFIG = "docker_config"
    DOCKER_RATELIMIT = "docker_ratelimit"
    FATAL_ERROR = "fatal_error"
    FREE_SPACE = "free_space"
    IPV4_CONNECTION_PROBLEM = "ipv4_connection_problem"
    MISSING_IMAGE = "missing_image"
    MOUNT_FAILED = "mount_failed"
    MULTIPLE_DATA_DISKS = "multiple_data_disks"
    NO_CURRENT_BACKUP = "no_current_backup"
    PWNED = "pwned"
    REBOOT_REQUIRED = "reboot_required"
    SECURITY = "security"
    TRUST = "trust"
    UPDATE_FAILED = "update_failed"
    UPDATE_ROLLBACK = "update_rollback"


class SuggestionType(StrEnum):
    """Sugestion type."""

    ADOPT_DATA_DISK = "adopt_data_disk"
    CLEAR_FULL_BACKUP = "clear_full_backup"
    CREATE_FULL_BACKUP = "create_full_backup"
    DISABLE_BOOT = "disable_boot"
    EXECUTE_INTEGRITY = "execute_integrity"
    EXECUTE_REBOOT = "execute_reboot"
    EXECUTE_REBUILD = "execute_rebuild"
    EXECUTE_RELOAD = "execute_reload"
    EXECUTE_REMOVE = "execute_remove"
    EXECUTE_REPAIR = "execute_repair"
    EXECUTE_RESET = "execute_reset"
    EXECUTE_RESTART = "execute_restart"
    EXECUTE_START = "execute_start"
    EXECUTE_STOP = "execute_stop"
    EXECUTE_UPDATE = "execute_update"
    REGISTRY_LOGIN = "registry_login"
    RENAME_DATA_DISK = "rename_data_disk"
