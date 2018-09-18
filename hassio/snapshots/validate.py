"""Validate some things around restore."""
import voluptuous as vol

from ..const import (
    ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_NAME, ATTR_SLUG, ATTR_DATE,
    ATTR_VERSION, ATTR_HOMEASSISTANT, ATTR_FOLDERS, ATTR_TYPE, ATTR_IMAGE,
    ATTR_PASSWORD, ATTR_PORT, ATTR_SSL, ATTR_WATCHDOG, ATTR_BOOT, ATTR_SIZE,
    ATTR_LAST_VERSION, ATTR_WAIT_BOOT, ATTR_PROTECTED, ATTR_CRYPTO,
    ATTR_REFRESH_TOKEN,
    FOLDER_SHARE, FOLDER_HOMEASSISTANT, FOLDER_ADDONS, FOLDER_SSL,
    SNAPSHOT_FULL, SNAPSHOT_PARTIAL, CRYPTO_AES128)
from ..validate import NETWORK_PORT, REPOSITORIES, DOCKER_IMAGE

ALL_FOLDERS = [FOLDER_HOMEASSISTANT, FOLDER_SHARE, FOLDER_ADDONS, FOLDER_SSL]


def unique_addons(addons_list):
    """Validate that an add-on is unique."""
    single = set(addon[ATTR_SLUG] for addon in addons_list)

    if len(single) != len(addons_list):
        raise vol.Invalid("Invalid addon list on snapshot!")
    return addons_list


# pylint: disable=no-value-for-parameter
SCHEMA_SNAPSHOT = vol.Schema({
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_TYPE): vol.In([SNAPSHOT_FULL, SNAPSHOT_PARTIAL]),
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_DATE): vol.Coerce(str),
    vol.Inclusive(ATTR_PROTECTED, 'encrypted'):
        vol.All(vol.Coerce(str), vol.Length(min=1, max=1)),
    vol.Inclusive(ATTR_CRYPTO, 'encrypted'): CRYPTO_AES128,
    vol.Optional(ATTR_HOMEASSISTANT, default=dict): vol.Schema({
        vol.Optional(ATTR_VERSION): vol.Coerce(str),
        vol.Inclusive(ATTR_IMAGE, 'custom_hass'): DOCKER_IMAGE,
        vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'): vol.Coerce(str),
        vol.Optional(ATTR_BOOT, default=True): vol.Boolean(),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_PORT, default=8123): NETWORK_PORT,
        vol.Optional(ATTR_PASSWORD): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_WATCHDOG, default=True): vol.Boolean(),
        vol.Optional(ATTR_WAIT_BOOT, default=600):
            vol.All(vol.Coerce(int), vol.Range(min=60)),
    }, extra=vol.REMOVE_EXTRA),
    vol.Optional(ATTR_FOLDERS, default=list):
        vol.All([vol.In(ALL_FOLDERS)], vol.Unique()),
    vol.Optional(ATTR_ADDONS, default=list): vol.All([vol.Schema({
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_VERSION): vol.Coerce(str),
        vol.Optional(ATTR_SIZE, default=0): vol.Coerce(float),
    }, extra=vol.REMOVE_EXTRA)], unique_addons),
    vol.Optional(ATTR_REPOSITORIES, default=list): REPOSITORIES,
}, extra=vol.ALLOW_EXTRA)
