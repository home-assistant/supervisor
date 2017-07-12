"""Represents known slave node instance."""

import asyncio
import json
import logging
from datetime import datetime

import aiohttp
import async_timeout

from .util import get_public_cluster_url, get_security_headers_raw
from ..api.util import hash_password
from ..const import (RUN_PING_CLUSTER_MASTER, JSON_DATA, JSON_RESULT,
                     RESULT_ERROR, JSON_MESSAGE, ATTR_CLUSTER_WRAP,
                     ATTR_ADDONS_REPOSITORIES)

_LOGGER = logging.getLogger(__name__)
INACTIVE_TIME = 2 * RUN_PING_CLUSTER_MASTER


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

    def _process_response(self, response):
        """Processing response from remote node."""
        if response is None or JSON_RESULT not in response:
            raise RuntimeError("Failed to call {0}".format(self.slug))
        if response[JSON_RESULT] == RESULT_ERROR:
            if JSON_MESSAGE in response and response[JSON_MESSAGE] is not None:
                msg = response[JSON_MESSAGE]
            else:
                msg = "Unknown error while calling {0}. " \
                      "Please check node logs".format(self.slug)
            raise RuntimeError(msg)
        if JSON_DATA not in response:
            return None
        return response[JSON_DATA]

    def _unwrap_cluster_response(self, response_data):
        """Unwrapping responses from remote node."""
        if response_data is None or ATTR_CLUSTER_WRAP not in response_data:
            raise RuntimeError("Failed to call {0}".format(self.slug))

        return response_data[ATTR_CLUSTER_WRAP]

    async def _do_post(self, url, data=None):
        """Performing post call to remote slave node."""
        try:
            url = get_public_cluster_url(self.last_ip, url)
            headers = get_security_headers_raw(self.hashed_key)

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.post(url,
                                                headers=headers,
                                                json=data) as response:
                    return self._process_response(await response.json(
                        content_type=None))
        except RuntimeError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.warning("Failed to POST cluster call %s : %s", url, err)
            raise RuntimeError("Failed to call {0}".format(self.slug))

    async def _do_get(self, url, is_raw=False):
        """Performing get call to remote slave node."""
        try:
            url = get_public_cluster_url(self.last_ip, url)
            headers = get_security_headers_raw(self.hashed_key)

            with async_timeout.timeout(10, loop=self.websession.loop):
                async with self.websession.get(url,
                                               headers=headers) as response:
                    if is_raw:
                        return bytearray(await response.text(), "utf8")
                    return self._process_response(
                        await response.json(content_type=None))
        except RuntimeError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError,
                KeyError, json.JSONDecodeError) as err:
            _LOGGER.warning("Failed to GET cluster call %s : %s", url, err)
            raise RuntimeError("Failed to call {0}".format(self.slug))

    @staticmethod
    def _get_addon_slug(request):
        """Retrieving addon slug from request."""
        slug = request.match_info.get("addon")
        if slug is None or slug == "":
            raise RuntimeError("Unknown addon")
        return slug

    def _get_addons_url(self, url, request):
        """Formatting addons url."""
        if url[0] != '/':
            url = "/" + url
        return "/addons/{0}{1}".format(self._get_addon_slug(request), url)

    def update_key(self, key):
        """Updating node key."""
        self.key = key
        self.hashed_key = hash_password(key)

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

    async def get_addons_list(self):
        """Retrieving addons list from remote slave node."""
        return self._unwrap_cluster_response(await self._do_get("/addons"))

    async def addon_info(self, request):
        """Retrieving addon information from remote slave node."""
        return await self._do_get(self._get_addons_url("/info", request))

    async def addon_options(self, request, body):
        """Updating addon options on remote slave node."""
        return await self._do_post(self._get_addons_url("/options", request),
                                   body)

    async def addon_install(self, request, body, config):
        """Installing addon on remote slave node."""
        body[ATTR_ADDONS_REPOSITORIES] = config.addons_repositories
        return await self._do_post(self._get_addons_url("/install", request),
                                   body)

    async def addon_uninstall(self, request):
        """Uninstalling addon on remote slave node."""
        return await self._do_post(self._get_addons_url("/uninstall", request))

    async def addon_start(self, request):
        """Starting addon on remote slave node."""
        return await self._do_post(self._get_addons_url("/start", request))

    async def addon_stop(self, request):
        """Stopping addon on remote slave node."""
        return await self._do_post(self._get_addons_url("/stop", request))

    async def addon_update(self, request, body):
        """Updating addin on remote slave node."""
        return await self._do_post(self._get_addons_url("/update", request),
                                   body)

    async def addon_restart(self, request):
        """Restarting addon on remote slave node."""
        return await self._do_post(self._get_addons_url("/restart", request))

    async def addon_logs(self, request):
        """Retrieving addon logs from remote slave node."""
        return await self._do_get(self._get_addons_url("/logs", request),
                                  is_raw=True)

    @property
    def last_seen(self):
        """Retrieving seconds from last seen."""
        if self.last_seen_time is None:
            return None
        return (datetime.utcnow() - self.last_seen_time).total_seconds()

    @property
    def is_active(self):
        """Flag indicating whether this node active or not."""
        passed = self.last_seen
        return passed is not None and passed < INACTIVE_TIME
