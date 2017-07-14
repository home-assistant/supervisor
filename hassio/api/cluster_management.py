"""Init file for HassIO cluster management rest api."""

import logging

import voluptuous as vol

from .cluster import APIClusterBase
from .util import get_real_ip
from ..cluster.util import (
    cluster_decrypt_schema, cluster_encrypt_json, cluster_public_api_process,
    cluster_encrypt_ok)
from ..const import (
    ATTR_NODE_KEY, ATTR_ADDONS_REPOSITORIES, ATTR_VERSION, ATTR_ARCH,
    ATTR_TIMEZONE, ATTR_NONCE, HTTP_HEADER_X_NODE, ATTR_ADDONS, ATTR_NAME)

_LOGGER = logging.getLogger(__name__)

SCHEMA_NONCE = vol.Schema({
    vol.Required(ATTR_NONCE): vol.Coerce(int),
})

SCHEMA_PING = SCHEMA_NONCE.extend({
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_ARCH): vol.Coerce(str),
    vol.Required(ATTR_TIMEZONE): vol.Coerce(str),
}, extra=True)

SCHEMA_NODE_REGISTER = vol.Schema({
    vol.Required(ATTR_NAME): vol.Coerce(str),
})


class APIClusterManagement(APIClusterBase):
    """Management part of cluster REST API."""

    def _get_calling_node(self, request):
        """Return known node based on public request data."""
        node = None
        if HTTP_HEADER_X_NODE in request.headers:
            node = self.cluster.get(request.headers.get(HTTP_HEADER_X_NODE))

        if node is None:
            raise RuntimeError("Requested node not found")
        return node

    @cluster_public_api_process
    async def ping(self, request):
        """Ping request from slave node."""
        self._master_only()
        node = self._get_calling_node(request)
        old_key = node.key
        body = await cluster_decrypt_schema(SCHEMA_PING, request, node.key)
        node.validate_nonce(body[ATTR_NONCE])
        new_key = self.cluster.sync(node,
                                    get_real_ip(request),
                                    body[ATTR_VERSION],
                                    body[ATTR_ARCH],
                                    body[ATTR_TIMEZONE],
                                    body[ATTR_ADDONS])
        response = {
            "result": True
        }

        if new_key is not None:
            response[ATTR_NODE_KEY] = new_key
        return cluster_encrypt_json(response, old_key)

    @cluster_public_api_process
    async def leave(self, request):
        """Un-registering slave node from cluster."""
        self._master_only()
        node = self._get_calling_node(request)
        body = await cluster_decrypt_schema(SCHEMA_NONCE, request, node.key)
        node.validate_nonce(body[ATTR_NONCE])
        _LOGGER.info("Node %s asked for un-register", node.slug)
        await self.cluster.remove_node(node, False)
        return cluster_encrypt_ok(node.key)

    @cluster_public_api_process
    async def register(self, request):
        """Registering new slave node into cluster."""
        self._master_only()
        body = await cluster_decrypt_schema(SCHEMA_NODE_REGISTER, request,
                                            self.cluster.master_key)
        ip_address = get_real_ip(request)
        node_key = self.cluster.register_node(ip_address, body[ATTR_NAME])
        return cluster_encrypt_json({
            ATTR_NODE_KEY: node_key,
            ATTR_ADDONS_REPOSITORIES: self.config.addons_repositories
        }, self.cluster.master_key)

    @cluster_public_api_process
    async def kick(self, request):
        """Processing cluster leave command from master."""
        await self._slave_only_body(request)
        _LOGGER.info("Received leave cluster command")
        return self._node_return(await self.cluster.switch_to_master(False))
