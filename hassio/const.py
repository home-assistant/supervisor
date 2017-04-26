"""Const file for HassIO."""
HASSIO_VERSION = '0.16'

URL_HASSIO_VERSION = ('https://raw.githubusercontent.com/home-assistant/'
                      'hassio/master/version.json')
URL_HASSIO_VERSION_BETA = ('https://raw.githubusercontent.com/home-assistant/'
                           'hassio/master/version_beta.json')

URL_HASSIO_ADDONS = 'https://github.com/home-assistant/hassio-addons'

DOCKER_REPO = "pvizeli"

HASSIO_SHARE = "/data"

RUN_UPDATE_INFO_TASKS = 28800
RUN_UPDATE_SUPERVISOR_TASKS = 29100
RUN_RELOAD_ADDONS_TASKS = 28800

RESTART_EXIT_CODE = 100

FILE_HASSIO_ADDONS = "{}/addons.json".format(HASSIO_SHARE)
FILE_HASSIO_CONFIG = "{}/config.json".format(HASSIO_SHARE)

SOCKET_DOCKER = "/var/run/docker.sock"
SOCKET_HC = "/var/run/hassio-hc.sock"

JSON_RESULT = 'result'
JSON_DATA = 'data'
JSON_MESSAGE = 'message'

RESULT_ERROR = 'error'
RESULT_OK = 'ok'

ATTR_HOSTNAME = 'hostname'
ATTR_TYPE = 'type'
ATTR_FEATURES = 'features'
ATTR_ADDONS = 'addons'
ATTR_VERSION = 'version'
ATTR_LAST_VERSION = 'last_version'
ATTR_BETA_CHANNEL = 'beta_channel'
ATTR_NAME = 'name'
ATTR_SLUG = 'slug'
ATTR_DESCRIPTON = 'description'
ATTR_STARTUP = 'startup'
ATTR_BOOT = 'boot'
ATTR_PORTS = 'ports'
ATTR_MAP_CONFIG = 'map_config'
ATTR_MAP_SSL = 'map_ssl'
ATTR_OPTIONS = 'options'
ATTR_INSTALLED = 'installed'
ATTR_DEDICATED = 'dedicated'
ATTR_STATE = 'state'
ATTR_SCHEMA = 'schema'
ATTR_IMAGE = 'image'

STARTUP_BEFORE = 'before'
STARTUP_AFTER = 'after'
STARTUP_ONCE = 'once'

BOOT_AUTO = 'auto'
BOOT_MANUAL = 'manual'

STATE_STARTED = 'started'
STATE_STOPPED = 'stopped'
