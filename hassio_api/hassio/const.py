"""Const file for HassIO."""
URL_SUPERVISOR_VERSION = \
    'https://raw.githubusercontent.com/pvizeli/hassio/master/version.json'

URL_ADDONS_REPO = 'https://github.com/pvizeli/hassio-addons'

FILE_RESIN_CONFIG = '/boot/config.json'
FILE_HASSIO_ADDONS = '/data/addons.json'
FILE_HASSIO_VERSION = '/data/version.json'

HOMEASSISTANT_CONFIG = '/resin-data/config'

HTTP_PORT = 9123

CONF_SUPERVISOR_IMAGE = 'supervisor_image'
CONF_SUPERVISOR_TAG = 'supervisor_tag'
CONF_HOMEASSISTANT_IMAGE = 'homeassistant_image'
CONF_HOMEASSISTANT_TAG = 'homeassistant_tag'
