"""Represents known slave node instance."""

import logging
import json
import asyncio
from datetime import datetime

import async_timeout
import aiohttp

from .util import get_public_cluster_url, get_security_headers_raw
from ..const import RUN_PING_CLUSTER_MASTER, ATTR_NODE, ATTR_ADDONS
from ..api.util import hash_password

_LOGGER = logging.getLogger(__name__)
INACTIVE_TIME = 2 * RUN_PING_CLUSTER_MASTER
RESPONSE_DATA = "data"


class ClusterNode(object):
    """Cluster node."""

    def __init__(self, slug, key, websession, ip_address=None):
        """Initialize new cluster node."""
        self.slug = slug
        self.key = key
        self.websession = websession
        self.hashed_key = hash_password(key)
        self.last_seen_time = None
        self.last_ip = ip_address
        self.version = None
        self.arch = None
        self.time_zone = None

    async def __do_post(self, url, data):
        """Performing post call to remote slave node."""
        try:
            url = get_public_cluster_url(self.last_ip, url)
            headers = get_security_headers_raw(self.hashed_key)

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.post(url,
                                                headers=headers,
                                                json=data) as request:
                    return await request.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.warning("Failed to POST cluster call %s : %s", url, err)
            return None

    async def __do_get(self, url):
        """Performing get call to remote slave node."""
        try:
            url = get_public_cluster_url(self.last_ip, url)
            headers = get_security_headers_raw(self.hashed_key)

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.get(url,
                                               headers=headers) as request:
                    return await request.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.warning("Failed to GET cluster call %s : %s", url, err)

    @staticmethod
    def __get_addon_slug(request):
        """Retrieving addon slug from request."""
        slug = request.match_info.get("addon")
        if slug is None or slug == "":
            raise RuntimeError("Unknown addon")
        return slug

    def ping(self, ip_address, version, arch, time_zone):
        """Updating information about remote node."""
        self.last_seen_time = datetime.utcnow()
        self.last_ip = ip_address
        self.version = version
        self.arch = arch
        self.time_zone = time_zone

    def validate_key(self, key):
        """Validating security key."""
        return self.hashed_key == key

    @property
    def is_active(self):
        """Flag indicating whether this node active or not."""
        seconds = (datetime.utcnow() - self.last_seen_time).total_seconds()
        return self.last_seen_time is not None and seconds < INACTIVE_TIME

    async def get_addons_list(self):
        """Retrieving addons list from remote slave node."""
        response = await self.__do_get("/addons")
        if response is None:
            _LOGGER.info("Failed to get addons from node %s", self.slug)
            return []

        if RESPONSE_DATA not in response \
                or ATTR_ADDONS not in response[RESPONSE_DATA]:
            _LOGGER.info("Unknown addons list response from node %s",
                         self.slug)
            return []
        for addon in response[RESPONSE_DATA][ATTR_ADDONS]:
            addon[ATTR_NODE] = self.slug
        return response[RESPONSE_DATA][ATTR_ADDONS]

    async def install_addon(self, original_request, body):
        """Installing addon on remote slave node."""
        return await self.__do_post(
            "/addons/{0}/install".format(
                self.__get_addon_slug(original_request)), body)
