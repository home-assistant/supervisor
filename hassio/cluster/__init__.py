"""Cluster manager object."""
import asyncio
import logging
import random

from .data import ClusterData
from .node import ClusterNode
from .util import api_broadcast
from .validate import (
    SCEHMA_BROADCAST_JOIN, SCHEMA_BROADCAST_LEAVE, SCHEMA_BROADCAST_RENEW,
    SCHEMA_BROADCAST_INFO, SCHEMA_BROADCAST_REPOSITORIES,
    SCHEMA_BROADCAST_RELOAD)
from ..const import (
    PORT_CLUSTER)
from ..tools import RestServer

_LOGGER = logging.getLogger(__name__)


class ClusterManager(RestServer):
    """Manage cluster."""

    def __init__(self, config, loop, websession, homeassistant, addons):
        """Initialize cluster manager."""
        super().__init__(self, loop, PORT_CLUSTER)
        self.config = config
        self.homeassistant = homeassistant
        self.websession = websession
        self.addons = addons
        self.data = ClusterData()

        self.nodes = {}

    @property
    def list_nodes(self):
        """Return list of nodes."""
        return set(self.nodes.keys())

    def prepare(self):
        """Init cluster data."""
        for slug in self._data.notes:
            self.nodes[slug] = ClusterNode(slug, self.data)

        # proxy commands
        self.webapp.router.add_post("/cluster/proxy/{d+}", self.api_proxy)

        # broadcasts
        self.webapp.router.add_post(
            "/cluster/broadcast/join", self.api_broadcast_join)
        self.webapp.router.add_post(
            "/cluster/broadcast/leave", self.api_broadcast_leave)
        self.webapp.router.add_post(
            "/cluster/broadcast/renew", self.api_broadcast_renew)
        self.webapp.router.add_post(
            "/cluster/broadcast/repositories", self.api_broadcast_repositories)
        self.webapp.router.add_post(
            "/cluster/broadcast/info", self.api_broadcast_info)
        self.webapp.router.add_post(
            "/cluster/broadcast/reload", self.api_broadcast_reload)

    @api_broadcast(SCHEMA_BROADCAST_JOIN)
    async def api_broadcast_join(self, request, data):
        """API broadcast/join commando."""
        node_slug = data[JSON_PAYLOAD][ATTR_NODE]
        ip = data[JSON_PAYLOAD][ATTR_IP]

        if node_slug in self.nodes:
            _LOGGER.warning("Receive join of exsits node!")
            return

    @api_broadcast(SCHEMA_BROADCAST_LEAVE)
    async def api_broadcast_leave(self, request, data):
        """API broadcast/leave commando."""

    @api_broadcast(SCHEMA_BROADCAST_RENEW)
    async def api_broadcast_renew(self, request, data):
        """API broadcast/renew commando."""
        node = self.get(data[JSON_PAYLOAD][ATTR_NODE])
        ip = data[JSON_PAYLOAD][ATTR_IP]

        if not node:
            _LOGGER.warning("Receive join of exsits node!")
            return

        if node.ip == node:
            return

        node.ip = ip
        self.data.level += 1

    @api_broadcast(SCHEMA_BROADCAST_REPOSITORIES)
    async def api_broadcast_repositories(self, request, data):
        """API broadcast/repositories commando."""

    @api_broadcast(SCHEMA_BROADCAST_INFO)
    async def api_broadcast_info(self, request, data):
        """API broadcast/info commando."""

    @api_broadcast(SCHEMA_BROADCAST_RELOAD)
    async def api_broadcast_info(self, request, data):
        """API broadcast/reload commando."""
