"""Constants file for Supervisor."""

from dataclasses import dataclass
from enum import StrEnum
from ipaddress import IPv4Network, IPv6Network
from pathlib import Path
from sys import version_info as systemversion
from typing import NotRequired, Self, TypedDict

from aiohttp import __version__ as aiohttpversion

SUPERVISOR_VERSION = "9999.09.9.dev9999"
SERVER_SOFTWARE = f"HomeAssistantSupervisor/{SUPERVISOR_VERSION} aiohttp/{aiohttpversion} Python/{systemversion[0]}.{systemversion[1]}"

DOCKER_PREFIX: str = "hassio"
OBSERVER_DOCKER_NAME: str = f"{DOCKER_PREFIX}_observer"
SUPERVISOR_DOCKER_NAME: str = f"{DOCKER_PREFIX}_supervisor"

URL_HASSIO_ADDONS = "https://github.com/home-assistant/addons"
URL_HASSIO_APPARMOR = "https://version.home-assistant.io/apparmor_{channel}.txt"
URL_HASSIO_VERSION = "https://version.home-assistant.io/{channel}.json"

SUPERVISOR_DATA = Path("/data")

FILE_HASSIO_ADDONS = Path(SUPERVISOR_DATA, "addons.json")
FILE_HASSIO_AUTH = Path(SUPERVISOR_DATA, "auth.json")
FILE_HASSIO_BACKUPS = Path(SUPERVISOR_DATA, "backups.json")
FILE_HASSIO_BOARD = Path(SUPERVISOR_DATA, "board.json")
FILE_HASSIO_CONFIG = Path(SUPERVISOR_DATA, "config.json")
FILE_HASSIO_DISCOVERY = Path(SUPERVISOR_DATA, "discovery.json")
FILE_HASSIO_DOCKER = Path(SUPERVISOR_DATA, "docker.json")
FILE_HASSIO_HOMEASSISTANT = Path(SUPERVISOR_DATA, "homeassistant.json")
FILE_HASSIO_INGRESS = Path(SUPERVISOR_DATA, "ingress.json")
FILE_HASSIO_SERVICES = Path(SUPERVISOR_DATA, "services.json")
FILE_HASSIO_UPDATER = Path(SUPERVISOR_DATA, "updater.json")
FILE_HASSIO_SECURITY = Path(SUPERVISOR_DATA, "security.json")

FILE_SUFFIX_CONFIGURATION = [".yaml", ".yml", ".json"]

MACHINE_ID = Path("/etc/machine-id")
SOCKET_DBUS = Path("/run/dbus/system_bus_socket")
SOCKET_DOCKER = Path("/run/docker.sock")
RUN_SUPERVISOR_STATE = Path("/run/supervisor")
SYSTEMD_JOURNAL_PERSISTENT = Path("/var/log/journal")
SYSTEMD_JOURNAL_VOLATILE = Path("/run/log/journal")

DOCKER_NETWORK = "hassio"
DOCKER_NETWORK_DRIVER = "bridge"
DOCKER_IPV6_NETWORK_MASK = IPv6Network("fd0c:ac1e:2100::/48")
DOCKER_IPV4_NETWORK_MASK = IPv4Network("172.30.32.0/23")
DOCKER_IPV4_NETWORK_RANGE = IPv4Network("172.30.33.0/24")

# This needs to match the dockerd --cpu-rt-runtime= argument.
DOCKER_CPU_RUNTIME_TOTAL = 950_000

# The rt runtimes are guarantees, hence we cannot allocate more
# time than available! Support up to 5 containers with equal time
# allocated.
# Note that the time is multiplied by CPU count. This means that
# a single container can schedule up to 950/5*4 = 760ms in RT priority
# on a quad core system.
DOCKER_CPU_RUNTIME_ALLOCATION = int(DOCKER_CPU_RUNTIME_TOTAL / 5)

DNS_SUFFIX = "local.hass.io"

LABEL_ARCH = "io.hass.arch"
LABEL_MACHINE = "io.hass.machine"
LABEL_TYPE = "io.hass.type"
LABEL_VERSION = "io.hass.version"

META_ADDON = "addon"
META_HOMEASSISTANT = "homeassistant"
META_SUPERVISOR = "supervisor"

JSON_DATA = "data"
JSON_MESSAGE = "message"
JSON_RESULT = "result"
JSON_JOB_ID = "job_id"
JSON_ERROR_KEY = "error_key"
JSON_EXTRA_FIELDS = "extra_fields"

RESULT_ERROR = "error"
RESULT_OK = "ok"

HEADER_REMOTE_USER_ID = "X-Remote-User-Id"
HEADER_REMOTE_USER_NAME = "X-Remote-User-Name"
HEADER_REMOTE_USER_DISPLAY_NAME = "X-Remote-User-Display-Name"
HEADER_TOKEN_OLD = "X-Hassio-Key"
HEADER_TOKEN = "X-Supervisor-Token"

ENV_HOMEASSISTANT_REPOSITORY = "HOMEASSISTANT_REPOSITORY"
ENV_SUPERVISOR_DEV = "SUPERVISOR_DEV"
ENV_SUPERVISOR_MACHINE = "SUPERVISOR_MACHINE"
ENV_SUPERVISOR_NAME = "SUPERVISOR_NAME"
ENV_SUPERVISOR_SHARE = "SUPERVISOR_SHARE"
ENV_SUPERVISOR_CPU_RT = "SUPERVISOR_CPU_RT"

REQUEST_FROM = "HASSIO_FROM"

ATTR_ACCESS_TOKEN = "access_token"
ATTR_ACCESSPOINTS = "accesspoints"
ATTR_ACTIVE = "active"
ATTR_ACTIVITY_LED = "activity_led"
ATTR_ADDON = "addon"
ATTR_ADDONS = "addons"
ATTR_ADDONS_CUSTOM_LIST = "addons_custom_list"
ATTR_ADDONS_REPOSITORIES = "addons_repositories"
ATTR_ADDR_GEN_MODE = "addr_gen_mode"
ATTR_ADDRESS = "address"
ATTR_ADDRESS_DATA = "address-data"
ATTR_ADMIN = "admin"
ATTR_ADVANCED = "advanced"
ATTR_APPARMOR = "apparmor"
ATTR_APPLICATION = "application"
ATTR_ARCH = "arch"
ATTR_ARGS = "args"
ATTR_AUDIO = "audio"
ATTR_AUDIO_INPUT = "audio_input"
ATTR_AUDIO_OUTPUT = "audio_output"
ATTR_AUTH = "auth"
ATTR_AUTH_API = "auth_api"
ATTR_AUTO = "auto"
ATTR_AUTO_UPDATE = "auto_update"
ATTR_AVAILABLE = "available"
ATTR_BACKUP = "backup"
ATTR_BACKUP_EXCLUDE = "backup_exclude"
ATTR_BACKUP_POST = "backup_post"
ATTR_BACKUP_PRE = "backup_pre"
ATTR_BACKUPS = "backups"
ATTR_BACKUPS_EXCLUDE_DATABASE = "backups_exclude_database"
ATTR_BLK_READ = "blk_read"
ATTR_BLK_WRITE = "blk_write"
ATTR_BOARD = "board"
ATTR_BOOT = "boot"
ATTR_BRANCH = "branch"
ATTR_BUILD = "build"
ATTR_BUILD_FROM = "build_from"
ATTR_CARD = "card"
ATTR_CHANGELOG = "changelog"
ATTR_CHANNEL = "channel"
ATTR_CHASSIS = "chassis"
ATTR_CHECKS = "checks"
ATTR_CLI = "cli"
ATTR_COMPRESSED = "compressed"
ATTR_CONFIG = "config"
ATTR_CONFIGURATION = "configuration"
ATTR_CONNECTED = "connected"
ATTR_CONNECTIONS = "connections"
ATTR_CONTAINERS = "containers"
ATTR_CONTENT = "content"
ATTR_CONTENT_TRUST = "content_trust"
ATTR_COUNTRY = "country"
ATTR_CPE = "cpe"
ATTR_CPU_PERCENT = "cpu_percent"
ATTR_CRYPTO = "crypto"
ATTR_DATA = "data"
ATTR_DATE = "date"
ATTR_DAYS_UNTIL_STALE = "days_until_stale"
ATTR_DEBUG = "debug"
ATTR_DEBUG_BLOCK = "debug_block"
ATTR_DEFAULT = "default"
ATTR_DEPLOYMENT = "deployment"
ATTR_DESCRIPTON = "description"
ATTR_DETACHED = "detached"
ATTR_DETECT_BLOCKING_IO = "detect_blocking_io"
ATTR_DEVICES = "devices"
ATTR_DEVICETREE = "devicetree"
ATTR_DIAGNOSTICS = "diagnostics"
ATTR_DISCOVERY = "discovery"
ATTR_DISK = "disk"
ATTR_DISK_FREE = "disk_free"
ATTR_DISK_LED = "disk_led"
ATTR_DISK_LIFE_TIME = "disk_life_time"
ATTR_DISK_TOTAL = "disk_total"
ATTR_DISK_USED = "disk_used"
ATTR_DISPLAYNAME = "displayname"
ATTR_DNS = "dns"
ATTR_DOCKER = "docker"
ATTR_DOCKER_API = "docker_api"
ATTR_DOCUMENTATION = "documentation"
ATTR_DOMAINS = "domains"
ATTR_ENABLE = "enable"
ATTR_ENABLE_IPV6 = "enable_ipv6"
ATTR_ENABLED = "enabled"
ATTR_MTU = "mtu"
ATTR_ENVIRONMENT = "environment"
ATTR_EVENT = "event"
ATTR_EXCLUDE_DATABASE = "exclude_database"
ATTR_EXTRA = "extra"
ATTR_FEATURES = "features"
ATTR_FIELDS = "fields"
ATTR_FILENAME = "filename"
ATTR_FLAGS = "flags"
ATTR_FOLDERS = "folders"
ATTR_FORCE = "force"
ATTR_FORCE_SECURITY = "force_security"
ATTR_FREQUENCY = "frequency"
ATTR_FULL_ACCESS = "full_access"
ATTR_GATEWAY = "gateway"
ATTR_GPIO = "gpio"
ATTR_HASSIO_API = "hassio_api"
ATTR_HASSIO_ROLE = "hassio_role"
ATTR_HASSOS = "hassos"
ATTR_HASSOS_UNRESTRICTED = "hassos_unrestricted"
ATTR_HASSOS_UPGRADE = "hassos_upgrade"
ATTR_HEALTHY = "healthy"
ATTR_HEARTBEAT_LED = "heartbeat_led"
ATTR_HOMEASSISTANT = "homeassistant"
ATTR_HOMEASSISTANT_EXCLUDE_DATABASE = "homeassistant_exclude_database"
ATTR_HOMEASSISTANT_API = "homeassistant_api"
ATTR_HOST = "host"
ATTR_HOST_DBUS = "host_dbus"
ATTR_HOST_INTERNET = "host_internet"
ATTR_HOST_IPC = "host_ipc"
ATTR_HOST_NETWORK = "host_network"
ATTR_HOST_PID = "host_pid"
ATTR_HOST_UTS = "host_uts"
ATTR_HOSTNAME = "hostname"
ATTR_ICON = "icon"
ATTR_ID = "id"
ATTR_IMAGE = "image"
ATTR_IMAGES = "images"
ATTR_INDEX = "index"
ATTR_INGRESS = "ingress"
ATTR_INGRESS_ENTRY = "ingress_entry"
ATTR_INGRESS_PANEL = "ingress_panel"
ATTR_INGRESS_PORT = "ingress_port"
ATTR_INGRESS_TOKEN = "ingress_token"
ATTR_INGRESS_URL = "ingress_url"
ATTR_INGRESS_STREAM = "ingress_stream"
ATTR_INIT = "init"
ATTR_INITIALIZE = "initialize"
ATTR_INPUT = "input"
ATTR_INSTALLED = "installed"
ATTR_INTERFACE = "interface"
ATTR_INTERFACES = "interfaces"
ATTR_IP_ADDRESS = "ip_address"
ATTR_IP6_PRIVACY = "ip6_privacy"
ATTR_IPV4 = "ipv4"
ATTR_IPV6 = "ipv6"
ATTR_ISSUES = "issues"
ATTR_JOB_ID = "job_id"
ATTR_JOURNALD = "journald"
ATTR_KERNEL = "kernel"
ATTR_KERNEL_MODULES = "kernel_modules"
ATTR_LABELS = "labels"
ATTR_LAST_BOOT = "last_boot"
ATTR_LEGACY = "legacy"
ATTR_LLMNR = "llmnr"
ATTR_LOCALS = "locals"
ATTR_LOCATION = "location"
ATTR_LOGGING = "logging"
ATTR_LOGO = "logo"
ATTR_LONG_DESCRIPTION = "long_description"
ATTR_MAC = "mac"
ATTR_MACHINE = "machine"
ATTR_MACHINE_ID = "machine_id"
ATTR_MAINTAINER = "maintainer"
ATTR_MAP = "map"
ATTR_MDNS = "mdns"
ATTR_MEMORY_LIMIT = "memory_limit"
ATTR_MEMORY_PERCENT = "memory_percent"
ATTR_MEMORY_USAGE = "memory_usage"
ATTR_MESSAGE = "message"
ATTR_METHOD = "method"
ATTR_MODE = "mode"
ATTR_MULTICAST = "multicast"
ATTR_NAME = "name"
ATTR_NAMESERVERS = "nameservers"
ATTR_NETWORK = "network"
ATTR_NETWORK_DESCRIPTION = "network_description"
ATTR_NETWORK_RX = "network_rx"
ATTR_NETWORK_TX = "network_tx"
ATTR_OBSERVER = "observer"
ATTR_OPERATING_SYSTEM = "operating_system"
ATTR_OPTIONS = "options"
ATTR_OTA = "ota"
ATTR_OUTPUT = "output"
ATTR_PANEL_ADMIN = "panel_admin"
ATTR_PANEL_ICON = "panel_icon"
ATTR_PANEL_TITLE = "panel_title"
ATTR_PANELS = "panels"
ATTR_PARENT = "parent"
ATTR_PASSWORD = "password"
ATTR_PATH = "path"
ATTR_PLUGINS = "plugins"
ATTR_PORT = "port"
ATTR_PORTS = "ports"
ATTR_PORTS_DESCRIPTION = "ports_description"
ATTR_POWER_LED = "power_led"
ATTR_PREFIX = "prefix"
ATTR_PRIMARY = "primary"
ATTR_PRIORITY = "priority"
ATTR_PRIVILEGED = "privileged"
ATTR_PROTECTED = "protected"
ATTR_PROVIDERS = "providers"
ATTR_PSK = "psk"
ATTR_PWNED = "pwned"
ATTR_RATING = "rating"
ATTR_READY = "ready"
ATTR_REALTIME = "realtime"
ATTR_REFRESH_TOKEN = "refresh_token"
ATTR_REGISTRIES = "registries"
ATTR_REGISTRY = "registry"
ATTR_REPOSITORIES = "repositories"
ATTR_REPOSITORY = "repository"
ATTR_SCHEMA = "schema"
ATTR_SECURITY = "security"
ATTR_SERIAL = "serial"
ATTR_SERVERS = "servers"
ATTR_SERVICE = "service"
ATTR_SERVICES = "services"
ATTR_SESSION = "session"
ATTR_SESSION_DATA = "session_data"
ATTR_SESSION_DATA_USER = "user"
ATTR_SESSION_DATA_USER_ID = "user_id"
ATTR_SIGNAL = "signal"
ATTR_SIZE = "size"
ATTR_SIZE_BYTES = "size_bytes"
ATTR_SLUG = "slug"
ATTR_SOURCE = "source"
ATTR_SQUASH = "squash"
ATTR_SSID = "ssid"
ATTR_SSL = "ssl"
ATTR_STAGE = "stage"
ATTR_STARTUP = "startup"
ATTR_STATE = "state"
ATTR_STATIC = "static"
ATTR_STDIN = "stdin"
ATTR_STORAGE = "storage"
ATTR_STORAGE_DRIVER = "storage_driver"
ATTR_SUGGESTIONS = "suggestions"
ATTR_SUPERVISOR = "supervisor"
ATTR_SUPERVISOR_INTERNET = "supervisor_internet"
ATTR_SUPERVISOR_VERSION = "supervisor_version"
ATTR_SUPPORTED = "supported"
ATTR_SUPPORTED_ARCH = "supported_arch"
ATTR_SWAP_SIZE = "swap_size"
ATTR_SWAPPINESS = "swappiness"
ATTR_SYSTEM = "system"
ATTR_SYSTEM_MANAGED = "system_managed"
ATTR_SYSTEM_MANAGED_CONFIG_ENTRY = "system_managed_config_entry"
ATTR_TIMEOUT = "timeout"
ATTR_TIMEZONE = "timezone"
ATTR_TITLE = "title"
ATTR_TMPFS = "tmpfs"
ATTR_TOTP = "totp"
ATTR_TRANSLATIONS = "translations"
ATTR_TYPE = "type"
ATTR_UART = "uart"
ATTR_UDEV = "udev"
ATTR_ULIMITS = "ulimits"
ATTR_UNHEALTHY = "unhealthy"
ATTR_UNSAVED = "unsaved"
ATTR_UNSUPPORTED = "unsupported"
ATTR_UPDATE_AVAILABLE = "update_available"
ATTR_UPDATE_KEY = "update_key"
ATTR_URL = "url"
ATTR_USB = "usb"
ATTR_USER = "user"
ATTR_USER_LED = "user_led"
ATTR_USERNAME = "username"
ATTR_UUID = "uuid"
ATTR_VALID = "valid"
ATTR_VALUE = "value"
ATTR_VERSION = "version"
ATTR_VERSION_TIMESTAMP = "version_timestamp"
ATTR_VERSION_LATEST = "version_latest"
ATTR_VIDEO = "video"
ATTR_VLAN = "vlan"
ATTR_VOLUME = "volume"
ATTR_VPN = "vpn"
ATTR_WAIT_BOOT = "wait_boot"
ATTR_WATCHDOG = "watchdog"
ATTR_WEBUI = "webui"
ATTR_WIFI = "wifi"

PROVIDE_SERVICE = "provide"
NEED_SERVICE = "need"
WANT_SERVICE = "want"

ARCH_ARMHF = "armhf"
ARCH_ARMV7 = "armv7"
ARCH_AARCH64 = "aarch64"
ARCH_AMD64 = "amd64"
ARCH_I386 = "i386"

ARCH_ALL = [ARCH_ARMHF, ARCH_ARMV7, ARCH_AARCH64, ARCH_AMD64, ARCH_I386]

REPOSITORY_CORE = "core"
REPOSITORY_LOCAL = "local"

FOLDER_HOMEASSISTANT = "homeassistant"
FOLDER_SHARE = "share"
FOLDER_ADDONS = "addons/local"
FOLDER_SSL = "ssl"
FOLDER_MEDIA = "media"

CRYPTO_AES128 = "aes128"

SECURITY_PROFILE = "profile"
SECURITY_DEFAULT = "default"
SECURITY_DISABLE = "disable"

ROLE_DEFAULT = "default"
ROLE_HOMEASSISTANT = "homeassistant"
ROLE_BACKUP = "backup"
ROLE_MANAGER = "manager"
ROLE_ADMIN = "admin"

ROLE_ALL = [ROLE_DEFAULT, ROLE_HOMEASSISTANT, ROLE_BACKUP, ROLE_MANAGER, ROLE_ADMIN]


class AddonBootConfig(StrEnum):
    """Boot mode config for the add-on."""

    AUTO = "auto"
    MANUAL = "manual"
    MANUAL_ONLY = "manual_only"


class AddonBoot(StrEnum):
    """Boot mode for the add-on."""

    AUTO = "auto"
    MANUAL = "manual"

    @classmethod
    def _missing_(cls, value: object) -> Self | None:
        """Convert 'forced' config values to their counterpart."""
        if value == AddonBootConfig.MANUAL_ONLY:
            for member in cls:
                if member == AddonBoot.MANUAL:
                    return member
        return None


class AddonStartup(StrEnum):
    """Startup types of Add-on."""

    INITIALIZE = "initialize"
    SYSTEM = "system"
    SERVICES = "services"
    APPLICATION = "application"
    ONCE = "once"


class AddonStage(StrEnum):
    """Stage types of add-on."""

    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class AddonState(StrEnum):
    """State of add-on."""

    STARTUP = "startup"
    STARTED = "started"
    STOPPED = "stopped"
    UNKNOWN = "unknown"
    ERROR = "error"


class UpdateChannel(StrEnum):
    """Core supported update channels."""

    STABLE = "stable"
    BETA = "beta"
    DEV = "dev"


class CoreState(StrEnum):
    """Represent current loading state."""

    INITIALIZE = "initialize"
    SETUP = "setup"
    STARTUP = "startup"
    RUNNING = "running"
    FREEZE = "freeze"
    SHUTDOWN = "shutdown"
    STOPPING = "stopping"
    CLOSE = "close"


class LogLevel(StrEnum):
    """Logging level of system."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HostFeature(StrEnum):
    """Host feature."""

    HASSOS = "hassos"
    HOSTNAME = "hostname"
    NETWORK = "network"
    REBOOT = "reboot"
    SERVICES = "services"
    SHUTDOWN = "shutdown"
    TIMEDATE = "timedate"


class BusEvent(StrEnum):
    """Bus event type."""

    DOCKER_CONTAINER_STATE_CHANGE = "docker_container_state_change"
    DOCKER_IMAGE_PULL_UPDATE = "docker_image_pull_update"
    HARDWARE_NEW_DEVICE = "hardware_new_device"
    HARDWARE_REMOVE_DEVICE = "hardware_remove_device"
    SUPERVISOR_CONNECTIVITY_CHANGE = "supervisor_connectivity_change"
    SUPERVISOR_JOB_END = "supervisor_job_end"
    SUPERVISOR_JOB_START = "supervisor_job_start"
    SUPERVISOR_STATE_CHANGE = "supervisor_state_change"


class CpuArch(StrEnum):
    """Supported CPU architectures."""

    ARMV7 = "armv7"
    ARMHF = "armhf"
    AARCH64 = "aarch64"
    I386 = "i386"
    AMD64 = "amd64"


class IngressSessionDataUserDict(TypedDict):
    """Response object for ingress session user."""

    id: str
    username: NotRequired[str | None]
    # Name is an alias for displayname, only one should be used
    displayname: NotRequired[str | None]
    name: NotRequired[str | None]


@dataclass
class IngressSessionDataUser:
    """Format of an IngressSessionDataUser object."""

    id: str
    display_name: str | None = None
    username: str | None = None

    def to_dict(self) -> IngressSessionDataUserDict:
        """Get dictionary representation."""
        return IngressSessionDataUserDict(
            id=self.id, displayname=self.display_name, username=self.username
        )

    @classmethod
    def from_dict(cls, data: IngressSessionDataUserDict) -> Self:
        """Return object from dictionary representation."""
        return cls(
            id=data["id"],
            display_name=data.get("displayname") or data.get("name"),
            username=data.get("username"),
        )


class IngressSessionDataDict(TypedDict):
    """Response object for ingress session data."""

    user: IngressSessionDataUserDict


@dataclass
class IngressSessionData:
    """Format of an IngressSessionData object."""

    user: IngressSessionDataUser

    def to_dict(self) -> IngressSessionDataDict:
        """Get dictionary representation."""
        return IngressSessionDataDict(user=self.user.to_dict())

    @classmethod
    def from_dict(cls, data: IngressSessionDataDict) -> Self:
        """Return object from dictionary representation."""
        return cls(user=IngressSessionDataUser.from_dict(data["user"]))


STARTING_STATES = [
    CoreState.INITIALIZE,
    CoreState.STARTUP,
    CoreState.SETUP,
]

# States in which the API can be used (enforced by system_validation())
VALID_API_STATES = frozenset(
    {
        CoreState.STARTUP,
        CoreState.RUNNING,
        CoreState.FREEZE,
    }
)
