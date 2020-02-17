"""Constants file for Hass.io."""
from enum import Enum
from ipaddress import ip_network
from pathlib import Path

HASSIO_VERSION = "202"


URL_HASSIO_ADDONS = "https://github.com/home-assistant/hassio-addons"
URL_HASSIO_VERSION = "https://version.home-assistant.io/{channel}.json"
URL_HASSIO_APPARMOR = "https://version.home-assistant.io/apparmor.txt"

URL_HASSOS_OTA = (
    "https://github.com/home-assistant/operating-system/releases/download/"
    "{version}/hassos_{board}-{version}.raucb"
)

HASSIO_DATA = Path("/data")

FILE_HASSIO_AUTH = Path(HASSIO_DATA, "auth.json")
FILE_HASSIO_ADDONS = Path(HASSIO_DATA, "addons.json")
FILE_HASSIO_CONFIG = Path(HASSIO_DATA, "config.json")
FILE_HASSIO_HOMEASSISTANT = Path(HASSIO_DATA, "homeassistant.json")
FILE_HASSIO_UPDATER = Path(HASSIO_DATA, "updater.json")
FILE_HASSIO_SERVICES = Path(HASSIO_DATA, "services.json")
FILE_HASSIO_DISCOVERY = Path(HASSIO_DATA, "discovery.json")
FILE_HASSIO_INGRESS = Path(HASSIO_DATA, "ingress.json")
FILE_HASSIO_DNS = Path(HASSIO_DATA, "dns.json")

SOCKET_DOCKER = Path("/var/run/docker.sock")

DOCKER_NETWORK = "hassio"
DOCKER_NETWORK_MASK = ip_network("172.30.32.0/23")
DOCKER_NETWORK_RANGE = ip_network("172.30.33.0/24")

DNS_SERVERS = ["dns://1.1.1.1", "dns://9.9.9.9"]
DNS_SUFFIX = "local.hass.io"

LABEL_VERSION = "io.hass.version"
LABEL_ARCH = "io.hass.arch"
LABEL_TYPE = "io.hass.type"
LABEL_MACHINE = "io.hass.machine"

META_ADDON = "addon"
META_SUPERVISOR = "supervisor"
META_HOMEASSISTANT = "homeassistant"

JSON_RESULT = "result"
JSON_DATA = "data"
JSON_MESSAGE = "message"

RESULT_ERROR = "error"
RESULT_OK = "ok"

CONTENT_TYPE_BINARY = "application/octet-stream"
CONTENT_TYPE_PNG = "image/png"
CONTENT_TYPE_JSON = "application/json"
CONTENT_TYPE_TEXT = "text/plain"
CONTENT_TYPE_TAR = "application/tar"
CONTENT_TYPE_URL = "application/x-www-form-urlencoded"
COOKIE_INGRESS = "ingress_session"

HEADER_TOKEN = "X-Supervisor-Token"
HEADER_TOKEN_OLD = "X-Hassio-Key"

ENV_TOKEN_OLD = "HASSIO_TOKEN"
ENV_TOKEN = "SUPERVISOR_TOKEN"
ENV_TIME = "TZ"

REQUEST_FROM = "HASSIO_FROM"

ATTR_MACHINE = "machine"
ATTR_WAIT_BOOT = "wait_boot"
ATTR_DEPLOYMENT = "deployment"
ATTR_WATCHDOG = "watchdog"
ATTR_CHANGELOG = "changelog"
ATTR_LOGGING = "logging"
ATTR_DATE = "date"
ATTR_ARCH = "arch"
ATTR_LONG_DESCRIPTION = "long_description"
ATTR_HOSTNAME = "hostname"
ATTR_TIMEZONE = "timezone"
ATTR_ARGS = "args"
ATTR_OPERATING_SYSTEM = "operating_system"
ATTR_CHASSIS = "chassis"
ATTR_TYPE = "type"
ATTR_SOURCE = "source"
ATTR_FEATURES = "features"
ATTR_ADDONS = "addons"
ATTR_PROVIDERS = "providers"
ATTR_VERSION = "version"
ATTR_VERSION_LATEST = "version_latest"
ATTR_AUTO_UART = "auto_uart"
ATTR_LAST_BOOT = "last_boot"
ATTR_LAST_VERSION = "last_version"
ATTR_LATEST_VERSION = "latest_version"
ATTR_CHANNEL = "channel"
ATTR_NAME = "name"
ATTR_SLUG = "slug"
ATTR_DESCRIPTON = "description"
ATTR_STARTUP = "startup"
ATTR_BOOT = "boot"
ATTR_PORTS = "ports"
ATTR_PORTS_DESCRIPTION = "ports_description"
ATTR_PORT = "port"
ATTR_SSL = "ssl"
ATTR_MAP = "map"
ATTR_WEBUI = "webui"
ATTR_OPTIONS = "options"
ATTR_INSTALLED = "installed"
ATTR_DETACHED = "detached"
ATTR_STATE = "state"
ATTR_SCHEMA = "schema"
ATTR_IMAGE = "image"
ATTR_ICON = "icon"
ATTR_LOGO = "logo"
ATTR_STDIN = "stdin"
ATTR_ADDONS_REPOSITORIES = "addons_repositories"
ATTR_REPOSITORY = "repository"
ATTR_REPOSITORIES = "repositories"
ATTR_URL = "url"
ATTR_MAINTAINER = "maintainer"
ATTR_PASSWORD = "password"
ATTR_TOTP = "totp"
ATTR_INITIALIZE = "initialize"
ATTR_LOCATON = "location"
ATTR_BUILD = "build"
ATTR_DEVICES = "devices"
ATTR_ENVIRONMENT = "environment"
ATTR_HOST_NETWORK = "host_network"
ATTR_HOST_PID = "host_pid"
ATTR_HOST_IPC = "host_ipc"
ATTR_HOST_DBUS = "host_dbus"
ATTR_NETWORK = "network"
ATTR_NETWORK_DESCRIPTION = "network_description"
ATTR_TMPFS = "tmpfs"
ATTR_PRIVILEGED = "privileged"
ATTR_USER = "user"
ATTR_SYSTEM = "system"
ATTR_SNAPSHOTS = "snapshots"
ATTR_HOMEASSISTANT = "homeassistant"
ATTR_HASSIO = "hassio"
ATTR_HASSIO_API = "hassio_api"
ATTR_HOMEASSISTANT_API = "homeassistant_api"
ATTR_UUID = "uuid"
ATTR_FOLDERS = "folders"
ATTR_SIZE = "size"
ATTR_TYPE = "type"
ATTR_TIMEOUT = "timeout"
ATTR_AUTO_UPDATE = "auto_update"
ATTR_CUSTOM = "custom"
ATTR_VIDEO = "video"
ATTR_AUDIO = "audio"
ATTR_AUDIO_INPUT = "audio_input"
ATTR_AUDIO_OUTPUT = "audio_output"
ATTR_INPUT = "input"
ATTR_OUTPUT = "output"
ATTR_DISK = "disk"
ATTR_SERIAL = "serial"
ATTR_SECURITY = "security"
ATTR_BUILD_FROM = "build_from"
ATTR_SQUASH = "squash"
ATTR_GPIO = "gpio"
ATTR_LEGACY = "legacy"
ATTR_ADDONS_CUSTOM_LIST = "addons_custom_list"
ATTR_CPU_PERCENT = "cpu_percent"
ATTR_NETWORK_RX = "network_rx"
ATTR_NETWORK_TX = "network_tx"
ATTR_MEMORY_LIMIT = "memory_limit"
ATTR_MEMORY_USAGE = "memory_usage"
ATTR_MEMORY_PERCENT = "memory_percent"
ATTR_BLK_READ = "blk_read"
ATTR_BLK_WRITE = "blk_write"
ATTR_ADDON = "addon"
ATTR_AVAILABLE = "available"
ATTR_HOST = "host"
ATTR_USERNAME = "username"
ATTR_DISCOVERY = "discovery"
ATTR_CONFIG = "config"
ATTR_SERVICES = "services"
ATTR_SERVICE = "service"
ATTR_DISCOVERY = "discovery"
ATTR_PROTECTED = "protected"
ATTR_CRYPTO = "crypto"
ATTR_BRANCH = "branch"
ATTR_KERNEL = "kernel"
ATTR_APPARMOR = "apparmor"
ATTR_DEVICETREE = "devicetree"
ATTR_CPE = "cpe"
ATTR_BOARD = "board"
ATTR_HASSOS = "hassos"
ATTR_HASSOS_CLI = "hassos_cli"
ATTR_VERSION_CLI = "version_cli"
ATTR_VERSION_CLI_LATEST = "version_cli_latest"
ATTR_REFRESH_TOKEN = "refresh_token"
ATTR_ACCESS_TOKEN = "access_token"
ATTR_DOCKER_API = "docker_api"
ATTR_FULL_ACCESS = "full_access"
ATTR_PROTECTED = "protected"
ATTR_RATING = "rating"
ATTR_HASSIO_ROLE = "hassio_role"
ATTR_SUPERVISOR = "supervisor"
ATTR_AUTH_API = "auth_api"
ATTR_KERNEL_MODULES = "kernel_modules"
ATTR_SUPPORTED_ARCH = "supported_arch"
ATTR_INGRESS = "ingress"
ATTR_INGRESS_PORT = "ingress_port"
ATTR_INGRESS_ENTRY = "ingress_entry"
ATTR_INGRESS_TOKEN = "ingress_token"
ATTR_INGRESS_URL = "ingress_url"
ATTR_INGRESS_PANEL = "ingress_panel"
ATTR_PANEL_ICON = "panel_icon"
ATTR_PANEL_TITLE = "panel_title"
ATTR_PANEL_ADMIN = "panel_admin"
ATTR_TITLE = "title"
ATTR_ENABLE = "enable"
ATTR_IP_ADDRESS = "ip_address"
ATTR_SESSION = "session"
ATTR_ADMIN = "admin"
ATTR_PANELS = "panels"
ATTR_DEBUG = "debug"
ATTR_DEBUG_BLOCK = "debug_block"
ATTR_DNS = "dns"
ATTR_SERVERS = "servers"
ATTR_LOCALS = "locals"
ATTR_UDEV = "udev"
ATTR_VALUE = "value"
ATTR_SNAPSHOT_EXCLUDE = "snapshot_exclude"
ATTR_DOCUMENTATION = "documentation"
ATTR_ADVANCED = "advanced"
ATTR_STAGE = "stage"

PROVIDE_SERVICE = "provide"
NEED_SERVICE = "need"
WANT_SERVICE = "want"

STARTUP_INITIALIZE = "initialize"
STARTUP_SYSTEM = "system"
STARTUP_SERVICES = "services"
STARTUP_APPLICATION = "application"
STARTUP_ONCE = "once"

STARTUP_ALL = [
    STARTUP_ONCE,
    STARTUP_INITIALIZE,
    STARTUP_SYSTEM,
    STARTUP_SERVICES,
    STARTUP_APPLICATION,
]

BOOT_AUTO = "auto"
BOOT_MANUAL = "manual"

STATE_STARTED = "started"
STATE_STOPPED = "stopped"
STATE_NONE = "none"

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

PRIVILEGED_NET_ADMIN = "NET_ADMIN"
PRIVILEGED_SYS_ADMIN = "SYS_ADMIN"
PRIVILEGED_SYS_RAWIO = "SYS_RAWIO"
PRIVILEGED_IPC_LOCK = "IPC_LOCK"
PRIVILEGED_SYS_TIME = "SYS_TIME"
PRIVILEGED_SYS_NICE = "SYS_NICE"
PRIVILEGED_SYS_MODULE = "SYS_MODULE"
PRIVILEGED_SYS_RESOURCE = "SYS_RESOURCE"
PRIVILEGED_SYS_PTRACE = "SYS_PTRACE"
PRIVILEGED_DAC_READ_SEARCH = "DAC_READ_SEARCH"

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

FEATURES_SHUTDOWN = "shutdown"
FEATURES_REBOOT = "reboot"
FEATURES_HASSOS = "hassos"
FEATURES_HOSTNAME = "hostname"
FEATURES_SERVICES = "services"

ROLE_DEFAULT = "default"
ROLE_HOMEASSISTANT = "homeassistant"
ROLE_BACKUP = "backup"
ROLE_MANAGER = "manager"
ROLE_ADMIN = "admin"

ROLE_ALL = [ROLE_DEFAULT, ROLE_HOMEASSISTANT, ROLE_BACKUP, ROLE_MANAGER, ROLE_ADMIN]

CHAN_ID = "chan_id"
CHAN_TYPE = "chan_type"


class AddonStages(str, Enum):
    """Stage types of add-on."""

    STABLE = "stable"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


class UpdateChannels(str, Enum):
    """Core supported update channels."""

    STABLE = "stable"
    BETA = "beta"
    DEV = "dev"
