"""Init file for HassIO cluster rest api."""
import logging
from collections import deque

import voluptuous as vol
from aiohttp import web

from .util import api_process, api_validate
from ..cluster.util import (
    cluster_decrypt_body_json, cluster_encrypt_json, cluster_encrypt,
    cluster_public_api_process)
from ..const import (
    ATTR_IS_MASTER, ATTR_MASTER_KEY, ATTR_SLUG, ATTR_NODE_KEY, ATTR_MASTER_IP,
    ATTR_VERSION, ATTR_ARCH, ATTR_TIMEZONE, ATR_KNOWN_NODES, ATTR_IP,
    ATTR_IS_ACTIVE, ATTR_LAST_SEEN, ATTR_NONCE, ATTR_CLUSTER_WRAP, ATTR_NAME)

_LOGGER = logging.getLogger(__name__)

SCHEMA_REGISTER = vol.Schema({
    vol.Required(ATTR_MASTER_KEY): vol.Coerce(str),
    vol.Required(ATTR_NAME): vol.Coerce(str),
    vol.Required(ATTR_MASTER_IP): vol.Coerce(str),
})


class APIClusterBase(object):
    """Base cluster API object."""

    def __init__(self, cluster, config, loop):
        """Initialize base cluster REST API object."""
        self.cluster = cluster
        self.config = config
        self.loop = loop
        self.nonce_queue = deque(maxlen=100)

    def _check_nonce(self, nonce):
        """Validating nonce received from master."""
        if nonce in self.nonce_queue:
            raise RuntimeError("Duplicated nonce from master")
        self.nonce_queue.append(nonce)

    def _master_only(self):
        """Check if this method is executed on master node."""
        if self.cluster.is_master is False:
            raise RuntimeError("Unable to execute on slave")

    async def _slave_only_body(self, request):
        """Check if this method is executed on slave node."""
        if self.cluster.is_master is True:
            raise RuntimeError("Unable to execute on master")
        result = await cluster_decrypt_body_json(request,
                                                 self.cluster.node_key)
        if ATTR_NONCE not in result:
            raise RuntimeError("Nonce not found")
        self._check_nonce(result[ATTR_NONCE])
        if ATTR_CLUSTER_WRAP in result:
            return result[ATTR_CLUSTER_WRAP]
        return {}

    def _node_return(self, json_obj):
        """Returning data back to master."""
        if isinstance(json_obj, web.Response):
            return cluster_encrypt(json_obj.text, self.cluster.node_key)
        if isinstance(json_obj, bool):
            return cluster_encrypt(str(json_obj), self.cluster.node_key)
        return cluster_encrypt_json(json_obj, self.cluster.node_key)

    @cluster_public_api_process
    async def proxy(self, request):
        """Proxy requests to internal REST API."""
        path = request.match_info.get("path")
        method = getattr(self._api_proxy, path)
        if method is None:
            raise RuntimeError(
                "Received unknown {0} command: {1}".format(
                    self._proxy_module, path))

        body = await self._slave_only_body(request)
        _LOGGER.info("Received remote %s command: %s",
                     self._proxy_module, path)

        # Check if we have overwrite for method
        wrapper = getattr(self, path, None)
        if wrapper is not None:
            return self._node_return(await wrapper(request, body))

        if method.__name__.endswith("cluster_wrap"):
            return self._node_return(await method(request, cluster_body=body))
        return self._node_return(await method(request))

    @property
    def _api_proxy(self):
        raise RuntimeError("API proxy is not defined")

    @property
    def _proxy_module(self):
        raise RuntimeError("Unknown proxy module")


class APICluster(APIClusterBase):
    """Handle rest api for cluster functions."""

    def _get_node(self, request):
        """Return known node based on request data."""
        slug = request.match_info.get("node")
        node = self.cluster.get(slug)
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
                    ATTR_NAME: node.name,
                    ATTR_ARCH: node.arch,
                    ATTR_VERSION: node.version,
                    ATTR_TIMEZONE: node.time_zone,
                    ATTR_IP: str(node.last_ip),
                    ATTR_IS_ACTIVE: node.is_active,
                    ATTR_LAST_SEEN: last_seen
                })

        else:
            response[ATTR_NAME] = self.cluster.node_name
            response[ATTR_NODE_KEY] = self.cluster.node_key
            response[ATTR_MASTER_IP] = self.cluster.master_ip

        return response

    @api_process
    async def leave(self, request):
        """Changing current node status to master."""
        await self.cluster.switch_to_master(True)
        return True

    @api_process
    async def register(self, request):
        """Changing current node status to slave."""
        body = await api_validate(SCHEMA_REGISTER, request)
        return await self.cluster.switch_to_slave(body[ATTR_MASTER_IP],
                                                  body[ATTR_MASTER_KEY],
                                                  body[ATTR_NAME])

    @api_process
    async def kick(self, request):
        """Removing existing slave node from cluster."""
        self._master_only()
        node = self._get_node(request)
        return await self.cluster.remove_node(node, True)
