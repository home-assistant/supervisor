"""Validate cluster options schema."""
import voluptuous as vol

from ..const import (
    ATTR_MASTER_KEY, ATTR_NODE, ATTR_MASTER_IP, ATTR_INITIALIZE, ATTR_MASTER,
    )

CLUSTER_MASTER_IP = 'master_ip'
CLUSTER_NODE_KEY = 'node_key'
CLUSTER_REGISTERED_NODES = 'registered_nodes'
CLUSTER_NODE_NAME = 'node_name'
CLUSTER_IS_MASTER = 'is_master'
CLUSTER_IS_INITED = "is_inited"

# pylint: disable=no-value-for-parameter
SCHEMA_CLUSTER_CONFIG = vol.Schema({
    vol.Optional(ATTR_INITIALIZE, default=False): vol.Boolean(),
    vol.Optional(ATTR_MASTER, default=True): vol.Boolean(),
    vol.Optional(ATTR_MASTER_KEY): vol.Coerce(str),
    vol.Optional(CLUSTER_MASTER_IP): vol.Coerce(str),
    vol.Optional(CLUSTER_NODE_KEY): vol.Coerce(str),
    vol.Optional(CLUSTER_NODE_NAME): vol.Coerce(str),
    vol.Optional(CLUSTER_REGISTERED_NODES, default={}):
        {vol.Coerce(str): vol.Schema({
            vol.Required(CLUSTER_NODE_NAME): vol.Coerce(str),
            vol.Required(CLUSTER_NODE_KEY): vol.Coerce(str),
        })},
})
