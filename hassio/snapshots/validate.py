"""Validate some things around restore."""

import voluptuous as vol

from ..const import (
    ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_NAME, ATTR_SLUG, ATTR_DATE,
    ATTR_VERSION, ATTR_HOMEASSISTANT, ATTR_FOLDERS, ATTR_TYPE, ATTR_DEVICES,
    FOLDER_SHARE, FOLDER_HOMEASSISTANT, FOLDER_ADDONS, FOLDER_SSL,
    SNAPSHOT_FULL, SNAPSHOT_PARTIAL)
from ..validate import hass_devices

ALL_FOLDERS = [FOLDER_HOMEASSISTANT, FOLDER_SHARE, FOLDER_ADDONS, FOLDER_SSL]

# pylint: disable=no-value-for-parameter
SCHEMA_SNAPSHOT = vol.Schema({
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_TYPE): vol.In([SNAPSHOT_FULL, SNAPSHOT_PARTIAL]),
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_DATE): vol.Coerce(str),
    vol.Required(ATTR_HOMEASSISTANT): vol.Schema({
        vol.Required(ATTR_VERSION): vol.Coerce(str),
        vol.Optional(ATTR_DEVICES, default=[]): hass_devices,
    }),
    vol.Optional(ATTR_FOLDERS, default=[]): [vol.In(ALL_FOLDERS)],
    vol.Optional(ATTR_ADDONS, default=[]): [vol.Schema({
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_VERSION): vol.Coerce(str),
    })],
    vol.Optional(ATTR_REPOSITORIES, default=[]): [vol.Url()],
}, extra=vol.ALLOW_EXTRA)
