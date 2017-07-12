"""Init file for HassIO cluster rest api."""
import logging

import voluptuous as vol

from .util import api_process, api_validate, hash_password
from ..const import (ATTR_IS_MASTER, ATTR_MASTER_KEY, ATTR_SLUG, ATTR_NODE_KEY,
                     ATTR_NODE_NAME, ATTR_MASTER_IP, HTTP_HEADER_X_NODE_KEY,
                     ATTR_VERSION, ATTR_ARCH, ATTR_TIMEZONE, ATR_KNOWN_NODES,
                     ATTR_IP, ATTR_IS_ACTIVE, ATTR_LAST_SEEN)

_LOGGER = logging.getLogger(__name__)

SCHEMA_SLAVE_SWITCH = vol.Schema({
    vol.Required(ATTR_MASTER_KEY): vol.Coerce(str),
    vol.Required(ATTR_NODE_NAME): vol.Coerce(str),
    vol.Required(ATTR_MASTER_IP): vol.Coerce(str),
})


class APIClusterBase(object):
    """Base cluster API object."""

    def __init__(self, cluster, config, loop):
        """Initialize base cluster REST API object."""
        self.cluster = cluster
        self.config = config
        self.loop = loop

    def _master_only(self):
        """Check if this method is executed on master node."""
        if self.cluster.is_master is False:
            raise RuntimeError("Unable to execute on slave")

    def _slave_only(self, request):
        """Check if this method is executed on slave node."""
        if self.cluster.is_master is True:
            raise RuntimeError("Unable to execute on master")

        if HTTP_HEADER_X_NODE_KEY not in request.headers \
                or request.headers.get(
                        HTTP_HEADER_X_NODE_KEY) != hash_password(
                            self.cluster.node_key):
            raise RuntimeError("Invalid node key")


class APICluster(APIClusterBase):
    """Handle rest api for cluster functions."""

    def _get_node(self, request):
        """Return known node based on request data."""
        slug = request.match_info.get("slug")
        node = self.cluster.get_node(slug)
        if node is None:
            raise RuntimeError("Requested node not found")
        return node

    @api_process
    async def info(self, request):
        """Return information about current cluster node."""
        is_master = self.cluster.is_master
        response = {
            ATTR_IS_MASTER: is_master
        }

        if is_master:
            response[ATTR_MASTER_KEY] = self.cluster.master_key
            response[ATR_KNOWN_NODES] = []
            for node in self.cluster.known_nodes:
                last_seen = int(node.last_seen) if node.last_seen is not None \
                    else None
                response[ATR_KNOWN_NODES].append({
                    ATTR_SLUG: node.slug,
                    ATTR_ARCH: node.arch,
                    ATTR_VERSION: node.version,
                    ATTR_TIMEZONE: node.time_zone,
                    ATTR_IP: str(node.last_ip),
                    ATTR_IS_ACTIVE: node.is_active,
                    ATTR_LAST_SEEN: last_seen
                })

        else:
            response[ATTR_NODE_NAME] = self.cluster.node_name
            response[ATTR_NODE_KEY] = self.cluster.node_key
            response[ATTR_MASTER_IP] = self.cluster.master_ip

        return response

    @api_process
    async def switch_to_master(self, request):
        """Changing current node status to master."""
        await self.cluster.switch_to_master()
        return True

    @api_process
    async def switch_to_slave(self, request):
        """Changing current node status to slave."""
        body = await api_validate(SCHEMA_SLAVE_SWITCH, request)
        return await self.cluster.switch_to_slave(body[ATTR_MASTER_IP],
                                                  body[ATTR_MASTER_KEY],
                                                  body[ATTR_NODE_NAME])

    @api_process
    async def remove_node(self, request):
        """Removing existing slave node from cluster."""
        self._master_only()
        node = self._get_node(request)
        return self.cluster.remove_node(node)
