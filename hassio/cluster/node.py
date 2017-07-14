"""Represents known slave node instance."""

import logging
from collections import deque
from datetime import datetime

from .util_rest import cluster_do_post, get_nonce_request
from ..api.util import hash_password
from ..const import (RUN_PING_CLUSTER_MASTER, JSON_DATA, JSON_RESULT,
                     RESULT_ERROR, JSON_MESSAGE, ATTR_CLUSTER_WRAP,
                     ATTR_ADDONS_REPOSITORIES)

_LOGGER = logging.getLogger(__name__)
INACTIVE_TIME = 2 * RUN_PING_CLUSTER_MASTER


class ClusterNode(object):
    """Cluster node."""

    def __init__(self, slug, name, key, websession, ip_address=None):
        """Initialize new cluster node."""
        self.slug = slug
        self.key = key
        self.name = name
        self.websession = websession
        self.hashed_key = hash_password(key)
        self.last_seen_time = None
        self.last_ip = ip_address
        self.version = None
        self.arch = None
        self.time_zone = None
        self.nonce_queue = deque(maxlen=100)
        self.addon_slugs = []
        self.addons = []

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

    async def _call_remote(self, url, json_obj=None, is_raw=False):
        """Performing REST call to remote slave node."""
        if json_obj is not None:
            nonce = get_nonce_request()
            nonce[ATTR_CLUSTER_WRAP] = json_obj
            json_obj = nonce
        result = await cluster_do_post(json_obj, self.last_ip, url, self.key,
                                       self.websession, is_raw=is_raw)
        if result is None:
            raise RuntimeError("Failed to call {0}".format(self.slug))

        if is_raw:
            return result
        return self._process_response(result)

    @staticmethod
    def _get_addons_url(url, request):
        """Formatting addons url."""
        if url[0] != '/':
            url = "/" + url
        slug = request.match_info.get("addon")
        if slug is None or slug == "":
            raise RuntimeError("Unknown addon")
        return "/addons/{0}{1}".format(slug, url)

    def update_key(self, key):
        """Updating node key."""
        self.key = key
        self.hashed_key = hash_password(key)

    def sync(self, ip_address, version, arch, time_zone):
        """Updating information about remote node."""
        self.last_seen_time = datetime.utcnow()
        self.last_ip = ip_address
        self.version = version
        self.arch = arch
        self.time_zone = time_zone

    def validate_key(self, key):
        """Validating security key."""
        return self.hashed_key == key

    async def addon_info(self, request):
        """Retrieving addon information from remote slave node."""
        return await self._call_remote(self._get_addons_url("/info", request))

    async def addon_options(self, request, body):
        """Updating addon options on remote slave node."""
        return await self._call_remote(self._get_addons_url("/options",
                                                            request), body)

    async def addon_install(self, request, body, config):
        """Installing addon on remote slave node."""
        body[ATTR_ADDONS_REPOSITORIES] = config.addons_repositories
        return await self._call_remote(self._get_addons_url("/install",
                                                            request), body)

    async def addon_uninstall(self, request):
        """Uninstalling addon on remote slave node."""
        return await self._call_remote(self._get_addons_url("/uninstall",
                                                            request))

    async def addon_start(self, request):
        """Starting addon on remote slave node."""
        return await self._call_remote(self._get_addons_url("/start", request))

    async def addon_stop(self, request):
        """Stopping addon on remote slave node."""
        return await self._call_remote(self._get_addons_url("/stop", request))

    async def addon_update(self, request, body):
        """Updating addin on remote slave node."""
        return await self._call_remote(self._get_addons_url("/update",
                                                            request), body)

    async def addon_restart(self, request):
        """Restarting addon on remote slave node."""
        return await self._call_remote(self._get_addons_url("/restart",
                                                            request))

    async def addon_logs(self, request):
        """Retrieving addon logs from remote slave node."""
        return await self._call_remote(self._get_addons_url("/logs", request),
                                       is_raw=True)

    async def leave_remote(self):
        """Passing leave node from cluster command to slave node."""
        return await self._call_remote("/kick", is_raw=True)

    async def host_info(self):
        """Retrieving host information from remote node."""
        return await self._call_remote("/host/info")

    async def host_reboot(self):
        """Rebooting host OS on remote node."""
        return await self._call_remote("/host/reboot")

    async def host_shutdown(self):
        """Shutting down remote node."""
        return await self._call_remote("/host/shutdown")

    async def host_update(self, body):
        """Updating host OS on remote node."""
        return await self._call_remote("/host/update", body)

    def validate_nonce(self, nonce):
        """Validating nonce received from remote node."""
        if nonce in self.nonce_queue:
            raise RuntimeError(
                "Duplicated nonce for node {0}".format(self.slug))
        self.nonce_queue.append(nonce)

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
