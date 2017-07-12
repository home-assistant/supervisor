"""Validate cluster options schema."""
import voluptuous as vol

CLUSTER_MASTER_IP = 'master_ip'
CLUSTER_NODE_KEY = 'node_key'
CLUSTER_REGISTERED_NODES = 'registered_nodes'
CLUSTER_NODE_NAME = 'node_name'

SCHEMA_CLUSTER_CONFIG = vol.Schema({
    vol.Optional(CLUSTER_MASTER_IP, default=""): vol.Coerce(str),
    vol.Optional(CLUSTER_NODE_KEY, default=""): vol.Coerce(str),
    vol.Optional(CLUSTER_NODE_NAME, default=""): vol.Coerce(str),
    vol.Optional(CLUSTER_REGISTERED_NODES, default={}):
        {vol.Coerce(str): vol.Coerce(str)},
})
