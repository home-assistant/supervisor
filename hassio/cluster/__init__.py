"""Cluster manager object."""
import asyncio
import logging
import random

from .data import ClusterData
from .node import ClusterNode
from .util import generate_cluster_key, get_node_slug
from .util_rest import cluster_do_post, get_nonce_request
from .validate import SCHEMA_CLUSTER_CONFIG
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
