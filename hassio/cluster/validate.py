"""Validate cluster options schema."""
import voluptuous as vol

from ..const import (
    ATTR_MASTER_KEY, ATTR_NODES, ATTR_NODE, ATTR_IP, ATTR_NAME, ATTR_SLUG,
    ATTR_LEVEL, ATTR_LAST_SEEN, ATTR_ACTIVE, ATTR_REPOSITORIES ATTR_ADDONS)


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
            vol.Required(ATTR_LAST_SEEN): vol.Coerce(int),
        })
    }),
})


SCHEMA_CLUSTER = vol.Schema({
    vol.Required(JSON_NODE): vol.Any(vol.Coerce(str), None),
    vol.Required(JSON_DATE): vol.Coerce(float),
    vol.Required(JSON_SALT): vol.Coerce(str),
    vol.Required(JSON_PAYLOAD): dict,
})

SCHEMA_BROADCAST_JOIN = SCHEMA_CLUSTER.extend({
    vol.Required(JSON_PAYLOAD): {
        vol.Required(ATTR_NODE): vol.Coerce(str),
        vol.Required(ATTR_IP): vol.Coerce(str),
    },
})

SCHEMA_BROADCAST_LEAVE = SCHEMA_CLUSTER.extend({
    vol.Required(JSON_PAYLOAD): {
        vol.Required(ATTR_NODE): vol.Coerce(str),
    },
})

# pylint: disable=no-value-for-parameter
SCHEMA_BROADCAST_REPOSITORIES = SCHEMA_CLUSTER.extend({
    vol.Required(JSON_PAYLOAD): {
        vol.Required(ATTR_REPOSITORIES): [vol.Url()],
    },
})

SCHEMA_BROADCAST_RENEW = SCHEMA_CLUSTER.extend({
    vol.Required(JSON_PAYLOAD): {
        vol.Required(ATTR_NODE): vol.Coerce(str),
        vol.Required(ATTR_NAME): vol.Coerce(str),
        vol.Required(ATTR_IP): vol.Coerce(str),
    },
})

SCEHMA_BROADCAST_RELOAD = SCHEMA_CLUSTER

SCHEMA_BROADCAST_INFO = SCHEMA_CLUSTER.extend({
    vol.Required(JSON_PAYLOAD): {
        vol.Required(ATTR_NODE): vol.Coerce(str),
        vol.Required(ATTR_LEVEL): vol.Coerce(int),
        vol.Required(ATTR_NODES): vol.Schema({
            vol.Coerce(str): vol.Any(vol.Coerce(str), None)
        }),
        vol.Required(ATTR_REPOSITORIES): [vol.Url()],
        vol.Required(ATTR_ADDONS): vol.Schema({
            vol.Coerce(str): vol.Coerce(str)
        }),
    },
})
