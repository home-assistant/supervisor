"""Bootstrap HassIO."""
import asyncio
import json
import os

from .const import (
    FILE_HASSIO_ADDONS, FILE_HASSIO_VERSION, FILE_RESIN_CONFIG,
    HOMEASSISTANT_CONFIG, CONF_SUPERVISOR_TAG, CONF_SUPERVISOR_IMAGE)


def initialize_system_data():
    """Setup default config and create folders."""
    # homeassistant config folder
    if not os.path.isdir(HOMEASSISTANT_CONFIG):
        os.mkdir(HOMEASSISTANT_CONFIG)

    # installed addons
    if not os.path.isfile(FILE_HASSIO_ADDONS):
        with open(FILE_HASSIO_ADDONS) as addons_file:
            addons_file.write(json.dumps({}))

    # supervisor/homeassistant image/tag versions
    versions = {}
    if not os.path.isfile(FILE_HASSIO_VERSION):
        versions.update({
            CONF_HOMEASSISTANT_IMAGE: os.environ['HOMEASSISTANT_REPOSITORY'],
            CONF_HOMEASSISTANT_TAG: '',
        })
    else:
        with open(FILE_HASSIO_VERSION, 'r') as conf_file:
            versions = json.loads(conf_file.read())

    # update version
    versions.update({
        CONF_SUPERVISOR_IMAGE: os.environ['SUPERVISOR_IMAGE'],
        CONF_SUPERVISOR_TAG: os.environ['SUPERVISOR_TAG'],
    })

    with open(FILE_HASSIO_VERSION, 'w') as conf_file:
        conf_file.write(json.dumps(versions))
