"""Validate some things around restore."""

import voluptuous as vol

from ..const import (
    ATTR_REPOSITORIES, ATTR_ADDONS, ATTR_NAME, ATTR_SLUG, ATTR_DATE,
    ATTR_VERSION, ATTR_HOMEASSISTANT, ATTR_FOLDERS, FOLDER_SHARE,
    FOLDER_CONFIG)

# pylint: disable=no-value-for-parameter
SCHEMA_SNAPSHOT = vol.Schema({
    vol.Required(ATTR_SLUG): vol.Coerce(str),
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_DATE): vol.Coerce(str),
    vol.Required(ATTR_HOMEASSISTANT): vol.Coerce(str),
    vol.Required(ATTR_FOLDERS): [vol.In([FOLDER_CONFIG, FOLDER_SHARE])],
    vol.Required(ATTR_ADDONS): [vol.Schema({
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_VERSION): vol.Coerce(str),
    })],
    vol.Required(ATTR_REPOSITORIES): [vol.Url()],
}, extra=vol.ALLOW_EXTRA)
