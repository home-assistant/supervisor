"""Init file for HassIO cluster rest api."""
import logging
import voluptuous as vol

from .util import api_process, api_validate, get_real_ip, get_addons_list, \
    hash_password
from ..const import (ATTR_IS_MASTER, ATTR_MASTER_KEY, ATTR_SLUG, ATTR_NODE_KEY,
                     ATTR_ADDONS_REPOSITORIES, ATTR_NODE_NAME, ATTR_MASTER_IP,
                     HTTP_HEADER_X_NODE_KEY, ATTR_VERSION, ATTR_ARCH,
                     ATTR_TIMEZONE, ATR_KNOWN_NODES, ATTR_IP, ATTR_IS_ACTIVE,
                     ATTR_ADDONS, ATTR_LAST_SEEN)

_LOGGER = logging.getLogger(__name__)

SCHEMA_SLAVE_SWITCH = vol.Schema({
    vol.Required(ATTR_MASTER_KEY): vol.Coerce(str),
    vol.Required(ATTR_NODE_NAME): vol.Coerce(str),
    vol.Required(ATTR_MASTER_IP): vol.Coerce(str),
})

SCHEMA_NODE_REGISTER = vol.Schema({
    vol.Required(ATTR_MASTER_KEY): vol.Coerce(str),
    vol.Required(ATTR_SLUG): vol.Coerce(str),
})

SCHEMA_PING = vol.Schema({
    vol.Required(ATTR_VERSION): vol.Coerce(str),
    vol.Required(ATTR_ARCH): vol.Coerce(str),
    vol.Required(ATTR_TIMEZONE): vol.Coerce(str),
})


class APICluster(object):
    """Handle rest api for cluster functions."""

    def __init__(self, config, addons, cluster, api_addons):
        """Initialize cluster REST API object."""
        self.cluster = cluster
        self.config = config
        self.addons = addons
        self.api_addons = api_addons

    def __master_only(self):
        """Check if this method is executed on master node."""
        if self.config.is_master is False:
            raise RuntimeError("Unable to execute on slave")

    def __slave_only(self, request):
        """Check if this method is executed on slave node."""
        if self.config.is_master is True:
            raise RuntimeError("Unable to execute on master")

        if HTTP_HEADER_X_NODE_KEY not in request.headers \
                or request.headers.get(
                    HTTP_HEADER_X_NODE_KEY) != hash_password(
                    self.config.node_key):
            raise RuntimeError("Invalid node key")

    def __get_node(self, request):
        """Return known node based on request data."""
        slug = request.match_info.get("slug")
        node = self.cluster.get_node(slug)
        if node is None:
            raise RuntimeError("Requested node not found")
        return node

    def __get_public_node(self, request):
        """Return known node based on public request data."""
        node = None
        if HTTP_HEADER_X_NODE_KEY in request.headers:
            node = self.cluster.get_public_node(
                request.headers.get(HTTP_HEADER_X_NODE_KEY))

        if node is None:
            raise RuntimeError("Requested node not found")
        return node

    @api_process
    async def info(self, request):
        """Return information about current cluster node."""
        is_master = self.config.is_master
        response = {
            ATTR_IS_MASTER: is_master
        }

        if is_master:
            response[ATTR_MASTER_KEY] = self.cluster.master_key
            response[ATR_KNOWN_NODES] = []
            for node in self.cluster.known_nodes:
                response[ATR_KNOWN_NODES].append({
                    ATTR_SLUG: node.slug,
                    ATTR_ARCH: node.arch,
                    ATTR_VERSION: node.version,
                    ATTR_TIMEZONE: node.time_zone,
                    ATTR_IP: str(node.last_ip),
                    ATTR_IS_ACTIVE: node.is_active,
                    ATTR_LAST_SEEN: node.last_seen
                })

        else:
            response[ATTR_SLUG] = self.config.node_slug
            response[ATTR_NODE_KEY] = self.config.node_key
            response[ATTR_MASTER_IP] = self.config.master_ip

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
    async def ping(self, request):
        """Ping request from slave node."""
        self.__master_only()
        body = await api_validate(SCHEMA_PING, request)
        node = self.__get_public_node(request)
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
    async def register_node(self, request):
        """Registering new slave node into cluster."""
        self.__master_only()
        body = await api_validate(SCHEMA_NODE_REGISTER, request)
        ip_address = get_real_ip(request)
        node_key = self.cluster.register_node(ip_address,
                                              body[ATTR_MASTER_KEY],
                                              body[ATTR_SLUG])
        return {
            ATTR_NODE_KEY: node_key,
            ATTR_ADDONS_REPOSITORIES: self.config.addons_repositories
        }

    @api_process
    async def unregister_node(self, request):
        """Un-registering slave node from cluster."""
        self.__master_only()
        node = self.__get_public_node(request)
        _LOGGER.info("Node %s asked for un-register", node.slug)
        return self.cluster.remove_node(node)

    @api_process
    async def remove_node(self, request):
        """Removing existing slave node from cluster."""
        self.__master_only()
        node = self.__get_node(request)
        return self.cluster.remove_node(node)

    @api_process
    async def get_addons_list(self, request):
        """Retrieving addons list from slave node."""
        self.__slave_only(request)
        return {
            ATTR_ADDONS: get_addons_list(self.addons,
                                         self.config,
                                         only_installed=True)
        }

    @api_process
    async def install_addon(self, request):
        """Installing addon on slave node."""
        self.__slave_only(request)
        _LOGGER.info("Remote addon installation called")
        await self.addons.load_addons()
        await self.api_addons.install(request)
