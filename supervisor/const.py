"""Constants file for Supervisor."""
from enum import Enum
from ipaddress import ip_network
from pathlib import Path

SUPERVISOR_VERSION = "241"

URL_HASSIO_ADDONS = "https://github.com/home-assistant/hassio-addons"
URL_HASSIO_APPARMOR = "https://version.home-assistant.io/apparmor.txt"
URL_HASSIO_VERSION = "https://version.home-assistant.io/{channel}.json"

URL_HASSOS_OTA = (
    "https://github.com/home-assistant/operating-system/releases/download/"
    "{version}/hassos_{board}-{version}.raucb"
)

SUPERVISOR_DATA = Path("/data")

FILE_HASSIO_ADDONS = Path(SUPERVISOR_DATA, "addons.json")
FILE_HASSIO_AUDIO = Path(SUPERVISOR_DATA, "audio.json")
FILE_HASSIO_AUTH = Path(SUPERVISOR_DATA, "auth.json")
FILE_HASSIO_CLI = Path(SUPERVISOR_DATA, "cli.json")
FILE_HASSIO_CONFIG = Path(SUPERVISOR_DATA, "config.json")
FILE_HASSIO_DISCOVERY = Path(SUPERVISOR_DATA, "discovery.json")
FILE_HASSIO_DNS = Path(SUPERVISOR_DATA, "dns.json")
FILE_HASSIO_HOMEASSISTANT = Path(SUPERVISOR_DATA, "homeassistant.json")
FILE_HASSIO_INGRESS = Path(SUPERVISOR_DATA, "ingress.json")
FILE_HASSIO_MULTICAST = Path(SUPERVISOR_DATA, "multicast.json")
FILE_HASSIO_SERVICES = Path(SUPERVISOR_DATA, "services.json")
FILE_HASSIO_UPDATER = Path(SUPERVISOR_DATA, "updater.json")

MACHINE_ID = Path("/etc/machine-id")
SOCKET_DBUS = Path("/run/dbus/system_bus_socket")
SOCKET_DOCKER = Path("/run/docker.sock")
RUN_SUPERVISOR_STATE = Path("/run/supervisor")

DOCKER_NETWORK = "hassio"
DOCKER_NETWORK_MASK = ip_network("172.30.32.0/23")
DOCKER_NETWORK_RANGE = ip_network("172.30.33.0/24")
DOCKER_IMAGE_DENYLIST = [
    "containrrr/watchtower",
    "pyouroboros/ouroboros",
    "v2tec/watchtower",
]

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

RESULT_ERROR = "error"
RESULT_OK = "ok"

CONTENT_TYPE_BINARY = "application/octet-stream"
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_PNG = "image/png"
CONTENT_TYPE_TAR = "application/tar"
CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_URL = "application/x-www-form-urlencoded"
COOKIE_INGRESS = "ingress_session"

HEADER_TOKEN = "X-Supervisor-Token"
HEADER_TOKEN_OLD = "X-Hassio-Key"

ENV_TIME = "TZ"
ENV_TOKEN = "SUPERVISOR_TOKEN"
ENV_TOKEN_OLD = "HASSIO_TOKEN"

ENV_HOMEASSISTANT_REPOSITORY = "HOMEASSISTANT_REPOSITORY"
ENV_SUPERVISOR_DEV = "SUPERVISOR_DEV"
ENV_SUPERVISOR_MACHINE = "SUPERVISOR_MACHINE"
ENV_SUPERVISOR_NAME = "SUPERVISOR_NAME"
ENV_SUPERVISOR_SHARE = "SUPERVISOR_SHARE"

REQUEST_FROM = "HASSIO_FROM"

ATTR_ACCESS_TOKEN = "access_token"
ATTR_ACTIVE = "active"
ATTR_ADDON = "addon"
ATTR_ADDONS = "addons"
ATTR_ADDONS_CUSTOM_LIST = "addons_custom_list"
ATTR_ADDONS_REPOSITORIES = "addons_repositories"
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
ATTR_AUTH_API = "auth_api"
ATTR_AUTO_UART = "auto_uart"
ATTR_AUTO_UPDATE = "auto_update"
ATTR_AVAILABLE = "available"
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
ATTR_CLI = "cli"
ATTR_CONFIG = "config"
ATTR_CONNECTIONS = "connections"
ATTR_CPE = "cpe"
ATTR_CPU_PERCENT = "cpu_percent"
ATTR_CRYPTO = "crypto"
ATTR_DATE = "date"
ATTR_DEBUG = "debug"
ATTR_DEBUG_BLOCK = "debug_block"
ATTR_DEFAULT = "default"
ATTR_DEPLOYMENT = "deployment"
ATTR_DESCRIPTON = "description"
ATTR_DETACHED = "detached"
ATTR_DEVICES = "devices"
ATTR_DEVICETREE = "devicetree"
ATTR_DIAGNOSTICS = "diagnostics"
ATTR_DISCOVERY = "discovery"
ATTR_DISK = "disk"
ATTR_DISK_FREE = "disk_free"
ATTR_DISK_TOTAL = "disk_total"
ATTR_DISK_USED = "disk_used"
ATTR_DNS = "dns"
ATTR_DOCKER = "docker"
ATTR_DOCKER_API = "docker_api"
ATTR_DOCUMENTATION = "documentation"
ATTR_DOMAINS = "domains"
ATTR_ENABLE = "enable"
ATTR_ENVIRONMENT = "environment"
ATTR_FEATURES = "features"
ATTR_FILENAME = "filename"
ATTR_FLAGS = "flags"
ATTR_FOLDERS = "folders"
ATTR_FULL_ACCESS = "full_access"
ATTR_GATEWAY = "gateway"
ATTR_GPIO = "gpio"
ATTR_HASSIO_API = "hassio_api"
ATTR_HASSIO_ROLE = "hassio_role"
ATTR_HASSOS = "hassos"
ATTR_HEALTHY = "healthy"
ATTR_HOMEASSISTANT = "homeassistant"
ATTR_HOMEASSISTANT_API = "homeassistant_api"
ATTR_HOST = "host"
ATTR_HOST_DBUS = "host_dbus"
ATTR_HOST_IPC = "host_ipc"
ATTR_HOST_NETWORK = "host_network"
ATTR_HOST_PID = "host_pid"
ATTR_HOSTNAME = "hostname"
ATTR_ICON = "icon"
ATTR_ID = "id"
ATTR_IMAGE = "image"
ATTR_INDEX = "index"
ATTR_INGRESS = "ingress"
ATTR_INGRESS_ENTRY = "ingress_entry"
ATTR_INGRESS_PANEL = "ingress_panel"
ATTR_INGRESS_PORT = "ingress_port"
ATTR_INGRESS_TOKEN = "ingress_token"
ATTR_INGRESS_URL = "ingress_url"
ATTR_INIT = "init"
ATTR_INITIALIZE = "initialize"
ATTR_INPUT = "input"
ATTR_INSTALLED = "installed"
ATTR_INTERFACE = "interface"
ATTR_INTERFACES = "interfaces"
ATTR_IP_ADDRESS = "ip_address"
ATTR_IPV4 = "ipv4"
ATTR_KERNEL = "kernel"
ATTR_KERNEL_MODULES = "kernel_modules"
ATTR_LAST_BOOT = "last_boot"
ATTR_LEGACY = "legacy"
ATTR_LOCALS = "locals"
ATTR_LOCATON = "location"
ATTR_LOGGING = "logging"
ATTR_LOGO = "logo"
ATTR_LONG_DESCRIPTION = "long_description"
ATTR_MACHINE = "machine"
ATTR_MAINTAINER = "maintainer"
ATTR_MAP = "map"
ATTR_MEMORY_LIMIT = "memory_limit"
ATTR_MEMORY_PERCENT = "memory_percent"
ATTR_MEMORY_USAGE = "memory_usage"
ATTR_MESSAGE = "message"
ATTR_METHOD = "method"
ATTR_METHODS = ["dhcp", "static"]
ATTR_MODE = "mode"
ATTR_MULTICAST = "multicast"
ATTR_NAME = "name"
ATTR_NAMESERVERS = "nameservers"
ATTR_NETWORK = "network"
ATTR_NETWORK_DESCRIPTION = "network_description"
ATTR_NETWORK_RX = "network_rx"
ATTR_NETWORK_TX = "network_tx"
ATTR_OPERATING_SYSTEM = "operating_system"
ATTR_OPTIONS = "options"
ATTR_OUTPUT = "output"
ATTR_PANEL_ADMIN = "panel_admin"
ATTR_PANEL_ICON = "panel_icon"
ATTR_PANEL_TITLE = "panel_title"
ATTR_PANELS = "panels"
ATTR_PASSWORD = "password"
ATTR_PORT = "port"
ATTR_PORTS = "ports"
ATTR_PORTS_DESCRIPTION = "ports_description"
ATTR_PREFIX = "prefix"
ATTR_PRIMARY = "primary"
ATTR_PRIORITY = "priority"
ATTR_PRIVILEGED = "privileged"
ATTR_PROTECTED = "protected"
ATTR_PROVIDERS = "providers"
ATTR_RATING = "rating"
ATTR_REFRESH_TOKEN = "refresh_token"
ATTR_REPOSITORIES = "repositories"
ATTR_REPOSITORY = "repository"
ATTR_SCHEMA = "schema"
ATTR_SECURITY = "security"
ATTR_SERIAL = "serial"
ATTR_SERVERS = "servers"
ATTR_SERVICE = "service"
ATTR_SERVICES = "services"
ATTR_SESSION = "session"
ATTR_SIZE = "size"
ATTR_SLUG = "slug"
ATTR_SNAPSHOT_EXCLUDE = "snapshot_exclude"
ATTR_SNAPSHOTS = "snapshots"
ATTR_SOURCE = "source"
ATTR_SQUASH = "squash"
ATTR_SSID = "ssid"
ATTR_SSL = "ssl"
ATTR_STAGE = "stage"
ATTR_STARTUP = "startup"
ATTR_STATE = "state"
ATTR_STATIC = "static"
ATTR_STDIN = "stdin"
ATTR_SUPERVISOR = "supervisor"
ATTR_SUPPORTED = "supported"
ATTR_SUPPORTED_ARCH = "supported_arch"
ATTR_SYSTEM = "system"
ATTR_TIMEOUT = "timeout"
ATTR_TIMEZONE = "timezone"
ATTR_TITLE = "title"
ATTR_TMPFS = "tmpfs"
ATTR_TOTP = "totp"
ATTR_TYPE = "type"
ATTR_UDEV = "udev"
ATTR_UNSAVED = "unsaved"
ATTR_URL = "url"
ATTR_USB = "usb"
ATTR_USER = "user"
ATTR_USERNAME = "username"
ATTR_UUID = "uuid"
ATTR_VALID = "valid"
ATTR_VALUE = "value"
ATTR_VERSION = "version"
ATTR_VERSION_LATEST = "version_latest"
ATTR_VIDEO = "video"
ATTR_VOLUME = "volume"
ATTR_VPN = "vpn"
ATTR_WAIT_BOOT = "wait_boot"
ATTR_WATCHDOG = "watchdog"
ATTR_WEBUI = "webui"

PROVIDE_SERVICE = "provide"
NEED_SERVICE = "need"
WANT_SERVICE = "want"

BOOT_AUTO = "auto"
BOOT_MANUAL = "manual"


MAP_CONFIG = "config"
MAP_SSL = "ssl"
MAP_ADDONS = "addons"
MAP_BACKUP = "backup"
MAP_SHARE = "share"

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

SNAPSHOT_FULL = "full"
SNAPSHOT_PARTIAL = "partial"

CRYPTO_AES128 = "aes128"

SECURITY_PROFILE = "profile"
SECURITY_DEFAULT = "default"
SECURITY_DISABLE = "disable"

PRIVILEGED_DAC_READ_SEARCH = "DAC_READ_SEARCH"
PRIVILEGED_IPC_LOCK = "IPC_LOCK"
PRIVILEGED_NET_ADMIN = "NET_ADMIN"
PRIVILEGED_SYS_ADMIN = "SYS_ADMIN"
PRIVILEGED_SYS_MODULE = "SYS_MODULE"
PRIVILEGED_SYS_NICE = "SYS_NICE"
PRIVILEGED_SYS_PTRACE = "SYS_PTRACE"
PRIVILEGED_SYS_RAWIO = "SYS_RAWIO"
PRIVILEGED_SYS_RESOURCE = "SYS_RESOURCE"
PRIVILEGED_SYS_TIME = "SYS_TIME"

PRIVILEGED_ALL = [
    PRIVILEGED_NET_ADMIN,
    PRIVILEGED_SYS_ADMIN,
    PRIVILEGED_SYS_RAWIO,
    PRIVILEGED_IPC_LOCK,
    PRIVILEGED_SYS_TIME,
    PRIVILEGED_SYS_NICE,
    PRIVILEGED_SYS_RESOURCE,
    PRIVILEGED_SYS_PTRACE,
    PRIVILEGED_SYS_MODULE,
    PRIVILEGED_DAC_READ_SEARCH,
]

ROLE_DEFAULT = "default"
ROLE_HOMEASSISTANT = "homeassistant"
ROLE_BACKUP = "backup"
ROLE_MANAGER = "manager"
ROLE_ADMIN = "admin"

ROLE_ALL = [ROLE_DEFAULT, ROLE_HOMEASSISTANT, ROLE_BACKUP, ROLE_MANAGER, ROLE_ADMIN]

CHAN_ID = "chan_id"
CHAN_TYPE = "chan_type"

SUPERVISED_SUPPORTED_OS = ["Debian GNU/Linux 10 (buster)"]


class AddonStartup(str, Enum):
    """Startup types of Add-on."""

    INITIALIZE = "initialize"
    SYSTEM = "system"
    SERVICES = "services"
    APPLICATION = "application"
    ONCE = "once"


class AddonStage(str, Enum):
    """Stage types of add-on."""

    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class AddonState(str, Enum):
    """State of add-on."""

    STARTED = "started"
    STOPPED = "stopped"
    UNKNOWN = "unknown"
    ERROR = "error"


class UpdateChannel(str, Enum):
    """Core supported update channels."""

    STABLE = "stable"
    BETA = "beta"
    DEV = "dev"


class CoreState(str, Enum):
    """Represent current loading state."""

    INITIALIZE = "initialize"
    SETUP = "setup"
    STARTUP = "startup"
    RUNNING = "running"
    FREEZE = "freeze"
    SHUTDOWN = "shutdown"
    STOPPING = "stopping"
    CLOSE = "close"


class LogLevel(str, Enum):
    """Logging level of system."""

    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class HostFeature(str, Enum):
    """Host feature."""

    HASSOS = "hassos"
    HOSTNAME = "hostname"
    NETWORK = "network"
    REBOOT = "reboot"
    SERVICES = "services"
    SHUTDOWN = "shutdown"
