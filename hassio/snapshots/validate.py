"""Validate some things around restore."""

import voluptuous as vol

from ..const import (
    ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_NAME, ATTR_SLUG, ATTR_DATE,
    ATTR_VERSION, ATTR_HOMEASSISTANT, ATTR_FOLDERS, ATTR_TYPE, FOLDER_SHARE,
    FOLDER_HOMEASSISTANT, FOLDER_ADDONS, FOLDER_SSL, SNAPSHOT_FULL,
    SNAPSHOT_PARTIAL)

ALL_FOLDERS = [FOLDER_HOMEASSISTANT, FOLDER_SHARE, FOLDER_ADDONS, FOLDER_SSL]

# pylint: disable=no-value-for-parameter
SCHEMA_SNAPSHOT = vol.Schema({
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_TYPE): vol.In([SNAPSHOT_FULL, SNAPSHOT_PARTIAL]),
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_DATE): vol.Coerce(str),
    vol.Required(ATTR_HOMEASSISTANT): vol.Coerce(str),
    vol.Required(ATTR_FOLDERS): [vol.In(ALL_FOLDERS)],
    vol.Required(ATTR_ADDONS): [vol.Schema({
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_VERSION): vol.Coerce(str),
    })],
    vol.Required(ATTR_REPOSITORIES): [vol.Url()],
}, extra=vol.ALLOW_EXTRA)
