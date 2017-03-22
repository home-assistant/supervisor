"""Const file for HassIO."""
import os

URL_SUPERVISOR_VERSION = \
    'https://raw.githubusercontent.com/pvizeli/hassio/master/version.json'

URL_ADDONS_REPO = 'https://github.com/pvizeli/hassio-addons'

FILE_RESIN_CONFIG = '/boot/config.json'
FILE_HASSIO_ADDONS = '/data/addons.json'
FILE_HASSIO_VERSION = '/data/version.json'

HASSIO_SHARE = os.environ['SUPERVISOR_SHARE']
HASSIO_DOCKER = os.environ['SUPERVISOR_NAME']

HOMEASSISTANT_CONFIG = "{}/homeassistant_config".format(HASSIO_SHARE)
HOMEASSISTANT_SSL = "{}/homeassistant_ssl".format(HASSIO_SHARE)

HTTP_PORT = 9123

CONF_SUPERVISOR_IMAGE = 'supervisor_image'
CONF_SUPERVISOR_TAG = 'supervisor_tag'
CONF_HOMEASSISTANT_IMAGE = 'homeassistant_image'
CONF_HOMEASSISTANT_TAG = 'homeassistant_tag'
