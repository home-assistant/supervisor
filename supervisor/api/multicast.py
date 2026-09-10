"""Init file for Supervisor Multicast RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ONE_SHOT,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..validate import version_tag
from .utils import api_process, api_return_stats, api_validate, require_running_system

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})


class APIMulticast(CoreSysAttributes):
    """Handle RESTful API for Multicast functions."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return Multicast information."""
        return {
            ATTR_VERSION: self.sys_plugins.multicast.version,
            ATTR_VERSION_LATEST: self.sys_plugins.multicast.latest_version,
            ATTR_UPDATE_AVAILABLE: self.sys_plugins.multicast.need_update,
        }

    @api_process
    async def stats(self, request: web.Request) -> dict[str, Any]:
        """Return resource information for v2 contract (always one-shot)."""
        stats = await self.sys_plugins.multicast.stats(one_shot=True)
        return api_return_stats(stats, legacy=False)

    @api_process
    async def stats_v1(self, request: web.Request) -> dict[str, Any]:
        """Return resource information."""
        one_shot = ATTR_ONE_SHOT in request.query
        stats = await self.sys_plugins.multicast.stats(one_shot=one_shot)

        return api_return_stats(stats, legacy=True)

    @api_process
    @require_running_system
    async def update(self, request: web.Request) -> None:
        """Update Multicast plugin."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_plugins.multicast.latest_version)

        if version == self.sys_plugins.multicast.version:
            raise APIError(f"Version {version} is already in use")
        await asyncio.shield(self.sys_plugins.multicast.update(version))

    @api_process
    @require_running_system
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Restart Multicast plugin."""
        return asyncio.shield(self.sys_plugins.multicast.restart())
