"""Validate cluster options schema."""
import voluptuous as vol

from ..const import (
    ATTR_MASTER_KEY, ATTR_NODES, ATTR_NODE, ATTR_IP, ATTR_NAME, ATTR_SLUG,
    ATTR_LEVEL, ATTR_LAST_SEEN, ATTR_ACTIVE)


# pylint: disable=no-value-for-parameter
SCHEMA_CLUSTER_CONFIG = vol.Schema({
    vol.Optional(ATTR_NODE, default={}): vol.Schema({
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_SLUG): vol.Coerce(str),
        vol.Required(ATTR_MASTER_KEY): vol.Coerce(str),
        vol.Required(ATTR_LEVEL): vol.Coerce(int),
    }),
    vol.Optional(ATTR_NODES, default={}): vol.Schema({
        vol.Coerce(str): vol.Schema({
            vol.Required(ATTR_NAME): vol.Coerce(str),
            vol.Required(ATTR_IP): vol.Coerce(str),
            vol.Required(ATTR_LAST_SEEN): vol.Coerce(str),
        })
    }),
})


SCHEMA_BROADCAST = vol.Schema({
    vol.Required(JSON_NODE): vol.Any(vol.Coerce(str), None),
    vol.Required(JSON_DATE): vol.Coerce(float),
    vol.Required(JSON_SALT): vol.Coerce(str),
    vol.Required(JSON_PAYLOAD): dict,
})
