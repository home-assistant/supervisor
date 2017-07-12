"""Init file for HassIO cluster addons management rest api."""

import asyncio
import logging

from hassio.const import ATTR_ADDONS_REPOSITORIES
from .cluster import APIClusterBase
from .util import api_process, get_addons_list, cluster_api_wrap, \
    api_process_raw, json_loads

_LOGGER = logging.getLogger(__name__)


class APIClusterAddons(APIClusterBase):
    """Addons management rest API on remote slave node."""
    def __init__(self, cluster, config, addons, api_addons, loop):
        """Initialize cluster REST API object."""
        super().__init__(cluster, config, loop)
        self.api_addons = api_addons
        self.addons = addons

    @api_process
    @cluster_api_wrap
    async def list(self, request):
        """Retrieving addons list from slave node."""
        self._slave_only(request)
        return get_addons_list(self.addons,
                               self.cluster.is_master,
                               only_installed=True)

    @api_process
    async def install(self, request):
        """Installing addon on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon install called")
        body = await request.json(loads=json_loads)
        tasks = []
        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            tasks.append(self.addons.load_repositories(new))
        tasks.append(self.api_addons.install_plain(request, body))

        results, _ = await asyncio.shield(
            asyncio.wait(tasks, loop=self.loop), loop=self.loop)
        last_result = None
        for result in results:
            err = result.exception()
            if err is not None:
                raise RuntimeError("Failed to install add-on, check node logs")
            last_result = result.result()

        return last_result

    async def uninstall(self, request):
        """Uninstalling addon on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon uninstall called")
        return await self.api_addons.uninstall(request)

    async def info(self, request):
        """Retrieving addon information from slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon info called")
        return await self.api_addons.info(request)

    async def start(self, request):
        """Starting addon on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon start called")
        return await self.api_addons.start(request)

    async def stop(self, request):
        """Stopping addon on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon stop called")
        return await self.api_addons.stop(request)

    async def restart(self, request):
        """Restarting addon on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon restart called")
        return await self.api_addons.restart(request)

    async def update(self, request):
        """Updating addon on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon update called")
        return await self.api_addons.update(request)

    async def options(self, request):
        """Updating addon options on slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon options called")
        return await self.api_addons.options(request)

    @api_process_raw
    async def logs(self, request):
        """Retrieving addon logs from slave node."""
        self._slave_only(request)
        _LOGGER.info("Remote addon logs called")
        return await self.api_addons.logs_plain(request)
