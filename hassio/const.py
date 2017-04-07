"""Const file for HassIO."""
HASSIO_VERSION = '0.5'

URL_HASSIO_VERSION = \
    'https://raw.githubusercontent.com/pvizeli/hassio/master/version.json'
URL_HASSIO_VERSION_BETA = \
    'https://raw.githubusercontent.com/pvizeli/hassio/master/version_beta.json'

URL_HASSIO_ADDONS = 'https://github.com/pvizeli/hassio-addons'

HASSIO_SHARE = "/data"

RUN_UPDATE_INFO_TASKS = 28800

FILE_HASSIO_ADDONS = "{}/addons.json".format(HASSIO_SHARE)
FILE_HASSIO_CONFIG = "{}/config.json".format(HASSIO_SHARE)

SOCKET_DOCKER = "/var/run/docker.sock"
SOCKET_HC = "/var/run/hassio-hc.sock"

JSON_RESULT = 'result'
JSON_DATA = 'data'
JSON_MESSAGE = 'message'

RESULT_ERROR = 'error'
RESULT_OK = 'ok'

ATTR_VERSION = 'version'
ATTR_CURRENT = 'current'
ATTR_BETA = 'beta'
