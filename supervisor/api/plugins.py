"""Common RESTful API endpoints shared by all Supervisor plugins."""

import asyncio
from collections.abc import Awaitable
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ONE_SHOT,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import APIError, PluginDisabledError
from ..plugins.base import PluginBase
from ..validate import version_tag
from .utils import api_process, api_return_stats, api_validate, require_running_system

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})


class APIPlugin[P: PluginBase](CoreSysAttributes):
    """Handle the RESTful API endpoints every plugin provides."""

    def __init__(self, coresys: CoreSys, plugin: P) -> None:
        """Initialize common plugin API."""
        self.coresys = coresys
        self.plugin: P = plugin

    def _info(self) -> dict[str, Any]:
        """Return plugin information, extended by plugins with their own fields."""
        return {
            ATTR_VERSION: self.plugin.version,
            ATTR_VERSION_LATEST: self.plugin.latest_version,
            ATTR_UPDATE_AVAILABLE: self.plugin.need_update,
        }

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return plugin information."""
        return self._info()

    @api_process
    async def stats(self, request: web.Request) -> dict[str, Any]:
        """Return resource information for v2 contract (always one-shot)."""
        stats = await self.plugin.stats(one_shot=True)
        return api_return_stats(stats, legacy=False)

    @api_process
    async def stats_v1(self, request: web.Request) -> dict[str, Any]:
        """Return resource information."""
        one_shot = ATTR_ONE_SHOT in request.query
        stats = await self.plugin.stats(one_shot=one_shot)

        return api_return_stats(stats, legacy=True)

    @api_process
    @require_running_system
    async def update(self, request: web.Request) -> None:
        """Update plugin."""
        if not self.plugin.enabled:
            raise PluginDisabledError(self.plugin.slug)

        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.plugin.latest_version)

        if not self.plugin.version:
            raise APIError(f"Plugin {self.plugin.slug} is not installed")
        if version == self.plugin.version:
            raise APIError(f"Version {version} is already in use")
        await asyncio.shield(self.plugin.update(version))

    @api_process
    @require_running_system
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Restart plugin."""
        return asyncio.shield(self.plugin.restart())
