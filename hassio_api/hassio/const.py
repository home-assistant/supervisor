"""Const file for HassIO."""
HASSIO_VERSION = '0.3'

URL_HASSIO_VERSION = \
    'https://raw.githubusercontent.com/pvizeli/hassio/master/version.json'

URL_ADDONS_REPO = 'https://github.com/pvizeli/hassio-addons'

FILE_HOST_CONFIG = '/boot/config.json'
FILE_HOST_NETWORK = '/boot/network'
FILE_HASSIO_ADDONS = '/data/addons.json'
FILE_HASSIO_CONFIG = '/data/config.json'

HASSIO_SHARE = '/data'

SOCKET_DOCKER = "/var/run/docker.sock"
SOCKET_HC = "/var/run/hassio-hc.sock"

HOMEASSISTANT_CONFIG = "{}/homeassistant_config"
HOMEASSISTANT_SSL = "{}/homeassistant_ssl"

HTTP_PORT = 9123

HOMEASSISTANT_IMAGE = 'homeassistant_image'
HOMEASSISTANT_TAG = 'homeassistant_tag'

ATTR_VERSION = 'version'
