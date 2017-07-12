"""Cluster manager object."""
import asyncio
import json
import logging
import random

import aiohttp
import async_timeout

from .validate import (SCHEMA_CLUSTER_CONFIG, CLUSTER_MASTER_IP,
                       CLUSTER_NODE_KEY, CLUSTER_NODE_NAME,
                       CLUSTER_REGISTERED_NODES)
from ..tools import JsonConfig
from .node import ClusterNode
from .util import (generate_cluster_key, get_node_slug,
                   get_public_cluster_url, get_security_headers)
from ..api.util import hash_password, get_addons_list
from ..const import (RUN_REGENERATE_CLUSTER_KEY, ATTR_MASTER_KEY, ATTR_SLUG,
                     ATTR_NODE_KEY, ATTR_ADDONS_REPOSITORIES,
                     RUN_PING_CLUSTER_MASTER, ATTR_VERSION, HASSIO_VERSION,
                     ATTR_TIMEZONE, ATTR_ARCH, JSON_DATA, FILE_HASSIO_CLUSTER,
                     ATTR_INSTALLED)

_LOGGER = logging.getLogger(__name__)


class ClusterManager(JsonConfig):
    """Manage cluster."""

    def __init__(self, config, loop, scheduler, websession,
                 homeassistant, addons):
        """Initialize cluster manager."""
        super().__init__(FILE_HASSIO_CLUSTER, SCHEMA_CLUSTER_CONFIG)
        self.config = config
        self.scheduler = scheduler
        self.homeassistant = homeassistant
        self.websession = websession
        self.addons = addons
        self.loop = loop
        self._master_key = None
        self.scheduler.register_task(
            self._regenerate_master_key, RUN_REGENERATE_CLUSTER_KEY, now=True)
        self.scheduler.register_task(
            self._ping_master, RUN_PING_CLUSTER_MASTER, now=True)

        self._lock = asyncio.Lock(loop=loop)

        self._nodes = []
        self._load_nodes()

    def _load_nodes(self):
        """Loading existing known nodes."""
        self._nodes.clear()
        for slug, key in self.registered_nodes:
            new_node = ClusterNode(slug, key, self.websession)
            self._nodes.append(new_node)

    def _find_node(self, slug=None, key=None):
        """Searching known node by slug or key."""
        for node_ in self._nodes:
            if slug is None:
                if node_.validate_key(key):
                    return node_
            else:
                if node_.slug == slug:
                    if key is None:
                        return node_
                    if node_.validate_key(key):
                        return node_
                    break
        return None

    async def _regenerate_master_key(self):
        """Periodically re-generating master key."""
        self._master_key = generate_cluster_key()

    async def _ping_master(self):
        if self.is_master is True:
            return
        try:
            url = get_public_cluster_url(self.master_ip, "/ping")
            headers = get_security_headers(self)

            data = {
                ATTR_VERSION: HASSIO_VERSION,
                ATTR_ARCH: self.config.arch,
                ATTR_TIMEZONE: self.config.timezone,
            }

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.post(url,
                                                headers=headers,
                                                json=data) as request:
                    response = await request.json(content_type=None)
                    if ATTR_NODE_KEY in response[JSON_DATA]:
                        node_key = response[JSON_DATA][ATTR_NODE_KEY]
                        self.node_key = node_key
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.warning("Failed to ping master %s", err)

    async def switch_to_master(self):
        """Switching operating mode to master."""
        if self.is_master is True:
            return
        self.is_master = True
        if await self.homeassistant.is_running() is False:
            _LOGGER.info("Starting HASS because of switching to master mode")
            await self.homeassistant.run()

        try:
            url = get_public_cluster_url(self.master_ip, "/unregister")
            headers = get_security_headers(self)

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.post(url,
                                                headers=headers) as request:
                    await request.json(content_type=None)
                    _LOGGER.info("Successfully un-registered on master")
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.error("Failed to un-register from master: %s", err)
            return False

    async def switch_to_slave(self, master_ip, master_key, node_name):
        """Switching operating mode to slave."""
        if self.is_master is False:
            return
        if await self.homeassistant.is_running():
            _LOGGER.info("Stopping HASS because of switching to slave mode")
            await self.homeassistant.stop()
        try:
            url = get_public_cluster_url(master_ip, "/register")
            data = {
                ATTR_MASTER_KEY: hash_password(master_key),
                ATTR_SLUG: get_node_slug(node_name)
            }

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.post(url, json=data) as request:
                    response = await request.json(content_type=None)
                    node_key = response[JSON_DATA][ATTR_NODE_KEY]
                    self.node_key = node_key
                    self.is_master = False
                    self.master_ip = master_ip
                    self.node_name = node_name

                    new = set(response[JSON_DATA][ATTR_ADDONS_REPOSITORIES])
                    await asyncio.shield(self.addons.load_repositories(new))

                    _LOGGER.info("Registered with %s, synced %d repositories",
                                 master_ip, len(new))
                    return True
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.error("Failed to register on master: %s", err)
            return False

    def register_node(self, ip_address, master_key, node_slug):
        """Registering new slave node."""
        if master_key != hash_password(self._master_key):
            _LOGGER.error("Attempt to register new node failed: wrong key")
            raise RuntimeError("Wrong key")

        if self._find_node(node_slug) is not None:
            _LOGGER.error("Attempt to re-register node %s", node_slug)
            raise RuntimeError("Node already registered")

        _LOGGER.info("Registered new node %s from IP %s",
                     node_slug, ip_address)
        node_key = generate_cluster_key()
        self.registered_nodes = (node_slug, node_key)
        new_node = ClusterNode(node_slug, node_key,
                               self.websession, ip_address)
        self._nodes.append(new_node)
        return node_key

    def remove_node(self, node_):
        """Removing known node from cluster."""
        self._nodes.remove(node_)
        self.registered_nodes = (node_.slug, None)
        _LOGGER.info("Removed node %s from cluster", node_.slug)
        return True

    def ping(self, node_, ip_address, version, arch, time_zone):
        """Responding to ping from slave node."""
        node_.ping(ip_address, version, arch, time_zone)
        new_key = None
        if random.SystemRandom().randint(1, 100) <= 20:
            new_key = generate_cluster_key()
            self.registered_nodes = (node_.slug, new_key)
            node_.update_key(new_key)
        return new_key

    def get_node(self, slug):
        """Retrieving known node by slug."""
        return self._find_node(slug=slug)

    def get_public_node(self, key):
        """Retreiving known node by hashed key."""
        return self._find_node(key=key)

    async def get_addons_list(self, only_installed=False):
        """Return a list of addons."""
        local = get_addons_list(self.addons,
                                self.is_master,
                                only_installed)
        if self.is_master is False:
            return local

        tasks = []
        for node_ in self.known_nodes:
            if node_.is_active:
                tasks.append(node_.get_addons_list())
        len_ = len(tasks)
        if len_ > 0:
            results, _ = await asyncio.shield(
                asyncio.wait(tasks, loop=self.loop), loop=self.loop)
            for result in results:
                err = result.exception()
                if err is not None:
                    _LOGGER.warning("Failed to fetch addons "
                                    "list from remote: %s", err)
                    continue
                for addon in result.result():
                    local_addon = next((x for x in local
                                        if x[ATTR_SLUG] == addon[ATTR_SLUG]),
                                       None)
                    if local_addon is not None:
                        local_addon[ATTR_INSTALLED] \
                            .update(addon[ATTR_INSTALLED])
                    else:
                        local.append(addon)
        return local

    @property
    def master_key(self):
        """Return current master key."""
        return self._master_key

    @property
    def known_nodes(self):
        """Return list of known nodes."""
        return self._nodes

    @property
    def master_ip(self):
        """Return master IP address."""
        return self._data.get(CLUSTER_MASTER_IP)

    @master_ip.setter
    def master_ip(self, value):
        """Set master IP address."""
        self._data[CLUSTER_MASTER_IP] = value
        self.save()

    @property
    def node_key(self):
        """Return node secret key."""
        return self._data.get(CLUSTER_NODE_KEY)

    @node_key.setter
    def node_key(self, value):
        """Set node secret key."""
        self._data[CLUSTER_NODE_KEY] = value
        self.save()

    @property
    def node_name(self):
        """Return node name."""
        return self._data[CLUSTER_NODE_NAME]

    @node_name.setter
    def node_name(self, value):
        """Set node name."""
        self._data[CLUSTER_NODE_NAME] = value
        self.save()

    @property
    def registered_nodes(self):
        """Return information about known nodes."""
        return self._data[CLUSTER_REGISTERED_NODES].items()

    @registered_nodes.setter
    def registered_nodes(self, value):
        """Set known node."""
        slug, key = value
        if key is None:
            self._data[CLUSTER_REGISTERED_NODES].pop(slug, None)
        else:
            self._data[CLUSTER_REGISTERED_NODES][slug] = key
        self.save()

    @property
    def is_master(self):
        """Return flag indicating whether this node operates as master."""
        return self.config.is_master

    @is_master.setter
    def is_master(self, value):
        """Set operation mode."""
        self.config.is_master = value
