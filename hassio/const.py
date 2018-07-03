"""Const file for HassIO."""
from pathlib import Path
from ipaddress import ip_network

HASSIO_VERSION = '114'

URL_HASSIO_ADDONS = "https://github.com/home-assistant/hassio-addons"
URL_HASSIO_VERSION = \
    "https://s3.amazonaws.com/hassio-version/{channel}.json"
URL_HASSIO_APPARMOR = \
    "https://s3.amazonaws.com/hassio-version/apparmor.txt"

URL_HASSOS_OTA = (
    "https://github.com/home-assistant/hassos/releases/download/"
    "{version}/hassos_{board}-{version}.raucb")

HASSIO_DATA = Path("/data")

FILE_HASSIO_ADDONS = Path(HASSIO_DATA, "addons.json")
FILE_HASSIO_CONFIG = Path(HASSIO_DATA, "config.json")
FILE_HASSIO_HOMEASSISTANT = Path(HASSIO_DATA, "homeassistant.json")
FILE_HASSIO_UPDATER = Path(HASSIO_DATA, "updater.json")
FILE_HASSIO_SERVICES = Path(HASSIO_DATA, "services.json")

SOCKET_DOCKER = Path("/var/run/docker.sock")

DOCKER_NETWORK = 'hassio'
DOCKER_NETWORK_MASK = ip_network('172.30.32.0/23')
DOCKER_NETWORK_RANGE = ip_network('172.30.33.0/24')

LABEL_VERSION = 'io.hass.version'
LABEL_ARCH = 'io.hass.arch'
LABEL_TYPE = 'io.hass.type'
LABEL_MACHINE = 'io.hass.machine'

META_ADDON = 'addon'
META_SUPERVISOR = 'supervisor'
META_HOMEASSISTANT = 'homeassistant'

JSON_RESULT = 'result'
JSON_DATA = 'data'
JSON_MESSAGE = 'message'

RESULT_ERROR = 'error'
RESULT_OK = 'ok'

CONTENT_TYPE_BINARY = 'application/octet-stream'
CONTENT_TYPE_PNG = 'image/png'
CONTENT_TYPE_JSON = 'application/json'
CONTENT_TYPE_TEXT = 'text/plain'
CONTENT_TYPE_TAR = 'application/tar'
HEADER_HA_ACCESS = 'x-ha-access'
HEADER_TOKEN = 'X-HASSIO-KEY'

ENV_TOKEN = 'HASSIO_TOKEN'
ENV_TIME = 'TZ'

REQUEST_FROM = 'HASSIO_FROM'

ATTR_MACHINE = 'machine'
ATTR_WAIT_BOOT = 'wait_boot'
ATTR_DEPLOYMENT = 'deployment'
ATTR_WATCHDOG = 'watchdog'
ATTR_CHANGELOG = 'changelog'
ATTR_DATE = 'date'
ATTR_ARCH = 'arch'
ATTR_LONG_DESCRIPTION = 'long_description'
ATTR_HOSTNAME = 'hostname'
ATTR_TIMEZONE = 'timezone'
ATTR_ARGS = 'args'
ATTR_OPERATING_SYSTEM = 'operating_system'
ATTR_CHASSIS = 'chassis'
ATTR_TYPE = 'type'
ATTR_SOURCE = 'source'
ATTR_FEATURES = 'features'
ATTR_ADDONS = 'addons'
ATTR_VERSION = 'version'
ATTR_VERSION_LATEST = 'version_latest'
ATTR_AUTO_UART = 'auto_uart'
ATTR_LAST_BOOT = 'last_boot'
ATTR_LAST_VERSION = 'last_version'
ATTR_CHANNEL = 'channel'
ATTR_NAME = 'name'
ATTR_SLUG = 'slug'
ATTR_DESCRIPTON = 'description'
ATTR_STARTUP = 'startup'
ATTR_BOOT = 'boot'
ATTR_PORTS = 'ports'
ATTR_PORT = 'port'
ATTR_SSL = 'ssl'
ATTR_MAP = 'map'
ATTR_WEBUI = 'webui'
ATTR_OPTIONS = 'options'
ATTR_INSTALLED = 'installed'
ATTR_DETACHED = 'detached'
ATTR_STATE = 'state'
ATTR_SCHEMA = 'schema'
ATTR_IMAGE = 'image'
ATTR_ICON = 'icon'
ATTR_LOGO = 'logo'
ATTR_STDIN = 'stdin'
ATTR_ADDONS_REPOSITORIES = 'addons_repositories'
ATTR_REPOSITORY = 'repository'
ATTR_REPOSITORIES = 'repositories'
ATTR_URL = 'url'
ATTR_MAINTAINER = 'maintainer'
ATTR_PASSWORD = 'password'
ATTR_TOTP = 'totp'
ATTR_INITIALIZE = 'initialize'
ATTR_SESSION = 'session'
ATTR_SESSIONS = 'sessions'
ATTR_LOCATON = 'location'
ATTR_BUILD = 'build'
ATTR_DEVICES = 'devices'
ATTR_ENVIRONMENT = 'environment'
ATTR_HOST_NETWORK = 'host_network'
ATTR_HOST_IPC = 'host_ipc'
ATTR_HOST_DBUS = 'host_dbus'
ATTR_NETWORK = 'network'
ATTR_TMPFS = 'tmpfs'
ATTR_PRIVILEGED = 'privileged'
ATTR_USER = 'user'
ATTR_SYSTEM = 'system'
ATTR_SNAPSHOTS = 'snapshots'
ATTR_HOMEASSISTANT = 'homeassistant'
ATTR_HASSIO = 'hassio'
ATTR_HASSIO_API = 'hassio_api'
ATTR_HOMEASSISTANT_API = 'homeassistant_api'
ATTR_UUID = 'uuid'
ATTR_FOLDERS = 'folders'
ATTR_SIZE = 'size'
ATTR_TYPE = 'type'
ATTR_TIMEOUT = 'timeout'
ATTR_AUTO_UPDATE = 'auto_update'
ATTR_CUSTOM = 'custom'
ATTR_AUDIO = 'audio'
ATTR_AUDIO_INPUT = 'audio_input'
ATTR_AUDIO_OUTPUT = 'audio_output'
ATTR_INPUT = 'input'
ATTR_OUTPUT = 'output'
ATTR_DISK = 'disk'
ATTR_SERIAL = 'serial'
ATTR_SECURITY = 'security'
ATTR_BUILD_FROM = 'build_from'
ATTR_SQUASH = 'squash'
ATTR_GPIO = 'gpio'
ATTR_LEGACY = 'legacy'
ATTR_ADDONS_CUSTOM_LIST = 'addons_custom_list'
ATTR_CPU_PERCENT = 'cpu_percent'
ATTR_NETWORK_RX = 'network_rx'
ATTR_NETWORK_TX = 'network_tx'
ATTR_MEMORY_LIMIT = 'memory_limit'
ATTR_MEMORY_USAGE = 'memory_usage'
ATTR_BLK_READ = 'blk_read'
ATTR_BLK_WRITE = 'blk_write'
ATTR_PROVIDER = 'provider'
ATTR_AVAILABLE = 'available'
ATTR_HOST = 'host'
ATTR_USERNAME = 'username'
ATTR_PROTOCOL = 'protocol'
ATTR_DISCOVERY = 'discovery'
ATTR_PLATFORM = 'platform'
ATTR_COMPONENT = 'component'
ATTR_CONFIG = 'config'
ATTR_DISCOVERY_ID = 'discovery_id'
ATTR_SERVICES = 'services'
ATTR_DISCOVERY = 'discovery'
ATTR_PROTECTED = 'protected'
ATTR_CRYPTO = 'crypto'
ATTR_BRANCH = 'branch'
ATTR_KERNEL = 'kernel'
ATTR_APPARMOR = 'apparmor'
ATTR_DEVICETREE = 'devicetree'
ATTR_CPE = 'cpe'
ATTR_BOARD = 'board'
ATTR_HASSOS = 'hassos'

SERVICE_MQTT = 'mqtt'

STARTUP_INITIALIZE = 'initialize'
STARTUP_SYSTEM = 'system'
STARTUP_SERVICES = 'services'
STARTUP_APPLICATION = 'application'
STARTUP_ONCE = 'once'

BOOT_AUTO = 'auto'
BOOT_MANUAL = 'manual'

STATE_STARTED = 'started'
STATE_STOPPED = 'stopped'
STATE_NONE = 'none'

MAP_CONFIG = 'config'
MAP_SSL = 'ssl'
MAP_ADDONS = 'addons'
MAP_BACKUP = 'backup'
MAP_SHARE = 'share'

ARCH_ARMHF = 'armhf'
ARCH_AARCH64 = 'aarch64'
ARCH_AMD64 = 'amd64'
ARCH_I386 = 'i386'

CHANNEL_STABLE = 'stable'
CHANNEL_BETA = 'beta'
CHANNEL_DEV = 'dev'

REPOSITORY_CORE = 'core'
REPOSITORY_LOCAL = 'local'

FOLDER_HOMEASSISTANT = 'homeassistant'
FOLDER_SHARE = 'share'
FOLDER_ADDONS = 'addons/local'
FOLDER_SSL = 'ssl'

SNAPSHOT_FULL = 'full'
SNAPSHOT_PARTIAL = 'partial'

CRYPTO_AES128 = 'aes128'

SECURITY_PROFILE = 'profile'
SECURITY_DEFAULT = 'default'
SECURITY_DISABLE = 'disable'

FEATURES_SHUTDOWN = 'shutdown'
FEATURES_REBOOT = 'reboot'
FEATURES_HASSOS = 'hassos'
FEATURES_HOSTNAME = 'hostname'
FEATURES_SERVICES = 'services'
