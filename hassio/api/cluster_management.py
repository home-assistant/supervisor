"""Init file for HassIO cluster management rest api."""

import logging

import voluptuous as vol

from .cluster import APIClusterBase
from .util import api_process, api_validate, get_real_ip
from ..const import (ATTR_MASTER_KEY, ATTR_SLUG, ATTR_NODE_KEY,
                     ATTR_ADDONS_REPOSITORIES, HTTP_HEADER_X_NODE_KEY,
                     ATTR_VERSION, ATTR_ARCH, ATTR_TIMEZONE)

_LOGGER = logging.getLogger(__name__)

SCHEMA_PING = vol.Schema({
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_ARCH): vol.Coerce(str),
    vol.Required(ATTR_TIMEZONE): vol.Coerce(str),
})

SCHEMA_NODE_REGISTER = vol.Schema({
    vol.Required(ATTR_MASTER_KEY): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
})


class APIClusterManagement(APIClusterBase):
    """Management part of cluster REST API."""

    def _get_public_node(self, request):
        """Return known node based on public request data."""
        node = None
        if HTTP_HEADER_X_NODE_KEY in request.headers:
            node = self.cluster.get_public_node(
                request.headers.get(HTTP_HEADER_X_NODE_KEY))

        if node is None:
            raise RuntimeError("Requested node not found")
        return node

    @api_process
    async def ping(self, request):
        """Ping request from slave node."""
        self._master_only()
        body = await api_validate(SCHEMA_PING, request)
        node = self._get_public_node(request)
        new_key = self.cluster.ping(node,
                                    get_real_ip(request),
                                    body[ATTR_VERSION],
                                    body[ATTR_ARCH],
                                    body[ATTR_TIMEZONE])
        response = {}
        if new_key is not None:
            response[ATTR_NODE_KEY] = new_key
        return response

    @api_process
    async def unregister_node(self, request):
        """Un-registering slave node from cluster."""
        self._master_only()
        node = self._get_public_node(request)
        _LOGGER.info("Node %s asked for un-register", node.slug)
        return self.cluster.remove_node(node)

    @api_process
    async def register_node(self, request):
        """Registering new slave node into cluster."""
        self._master_only()
        body = await api_validate(SCHEMA_NODE_REGISTER, request)
        ip_address = get_real_ip(request)
        node_key = self.cluster.register_node(ip_address,
                                              body[ATTR_MASTER_KEY],
                                              body[ATTR_SLUG])
        return {
            ATTR_NODE_KEY: node_key,
            ATTR_ADDONS_REPOSITORIES: self.config.addons_repositories
        }
