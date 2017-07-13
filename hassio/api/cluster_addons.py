"""Init file for HassIO cluster addons management rest api."""

import asyncio
import logging

from hassio.const import ATTR_ADDONS_REPOSITORIES
from .cluster import APIClusterBase
from ..cluster.util import cluster_public_api_process

_LOGGER = logging.getLogger(__name__)


class APIClusterAddons(APIClusterBase):
    """Addons management rest API on remote slave node."""

    def __init__(self, cluster, config, addons, api_addons, loop):
        """Initialize cluster REST API object."""
        super().__init__(cluster, config, loop)
        self.api_addons = api_addons
        self.addons = addons

    @cluster_public_api_process
    async def install(self, request):
        """Installing addon on slave node."""
        body = await self._slave_only_body(request)
        _LOGGER.info("Remote addon install called")
        tasks = []
        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            tasks.append(self.addons.load_repositories(new))
            body.pop(ATTR_ADDONS_REPOSITORIES, None)
        tasks.append(self.api_addons.install(request, cluster_body=body))

        results, _ = await asyncio.wait(tasks, loop=self.loop)
        last_result = None
        for result in results:
            err = result.exception()
            if err is not None:
                raise RuntimeError(err)
            last_result = result.result()

        return self._node_return(last_result)

    @cluster_public_api_process
    async def uninstall(self, request):
        """Uninstalling addon on slave node."""
        await self._slave_only_body(request)
        _LOGGER.info("Remote addon uninstall called")
        return self._node_return(await self.api_addons.uninstall(request))

    @cluster_public_api_process
    async def info(self, request):
        """Retrieving addon information from slave node."""
        await self._slave_only_body(request)
        _LOGGER.info("Remote addon info called")
        return self._node_return(await self.api_addons.info(
            request))

    @cluster_public_api_process
    async def start(self, request):
        """Starting addon on slave node."""
        await self._slave_only_body(request)
        _LOGGER.info("Remote addon start called")
        return self._node_return(await self.api_addons.start(request))

    @cluster_public_api_process
    async def stop(self, request):
        """Stopping addon on slave node."""
        await self._slave_only_body(request)
        _LOGGER.info("Remote addon stop called")
        return self._node_return(await self.api_addons.stop(request))

    @cluster_public_api_process
    async def restart(self, request):
        """Restarting addon on slave node."""
        await self._slave_only_body(request)
        _LOGGER.info("Remote addon restart called")
        return self._node_return(await self.api_addons.restart(request))

    @cluster_public_api_process
    async def update(self, request):
        """Updating addon on slave node."""
        body = await self._slave_only_body(request)
        _LOGGER.info("Remote addon update called")
        return self._node_return(await self.api_addons.update(
            request, cluster_body=body))

    @cluster_public_api_process
    async def options(self, request):
        """Updating addon options on slave node."""
        body = await self._slave_only_body(request)
        _LOGGER.info("Remote addon options called")
        return self._node_return(await self.api_addons.options(
            request, cluster_body=body))

    @cluster_public_api_process
    async def logs(self, request):
        """Retrieving addon logs from slave node."""
        await self._slave_only_body(request)
        _LOGGER.info("Remote addon logs called")
        return self._node_return(await self.api_addons.logs(request))
