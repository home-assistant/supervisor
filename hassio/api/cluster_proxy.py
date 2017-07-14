"""Init file for HassIO cluster addons management rest api."""

import asyncio
import logging

from hassio.const import ATTR_ADDONS_REPOSITORIES
from .cluster import APIClusterBase

_LOGGER = logging.getLogger(__name__)


class APIClusterAddons(APIClusterBase):
    """Addons management rest API on remote slave node."""

    def __init__(self, cluster, config, addons, api_addons, loop):
        """Initialize cluster REST API object."""
        super().__init__(cluster, config, loop)
        self.addons = addons
        self.api_addons = api_addons

    @property
    def _api_proxy(self):
        return self.api_addons

    @property
    def _proxy_module(self):
        return "addons"

    async def install(self, request, body):
        """Installing addon on slave node."""
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

        return last_result
