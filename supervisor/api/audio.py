"""Init file for Supervisor Audio RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_CPU_PERCENT,
    ATTR_HOST,
    ATTR_LATEST_VERSION,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_PERCENT,
    ATTR_MEMORY_USAGE,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_VERSION,
    CONTENT_TYPE_BINARY,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): vol.Coerce(str)})


class APIAudio(CoreSysAttributes):
    """Handle RESTful API for Audio functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return Audio information."""
        return {
            ATTR_VERSION: self.sys_audio.version,
            ATTR_LATEST_VERSION: self.sys_audio.latest_version,
            ATTR_HOST: str(self.sys_docker.network.audio),
        }

    @api_process
    async def stats(self, request: web.Request) -> Dict[str, Any]:
        """Return resource information."""
        stats = await self.sys_audio.stats()

        return {
            ATTR_CPU_PERCENT: stats.cpu_percent,
            ATTR_MEMORY_USAGE: stats.memory_usage,
            ATTR_MEMORY_LIMIT: stats.memory_limit,
            ATTR_MEMORY_PERCENT: stats.memory_percent,
            ATTR_NETWORK_RX: stats.network_rx,
            ATTR_NETWORK_TX: stats.network_tx,
            ATTR_BLK_READ: stats.blk_read,
            ATTR_BLK_WRITE: stats.blk_write,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update Audio plugin."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_audio.latest_version)

        if version == self.sys_audio.version:
            raise APIError("Version {} is already in use".format(version))
        await asyncio.shield(self.sys_audio.update(version))

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return Audio Docker logs."""
        return self.sys_audio.logs()

    @api_process
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Restart Audio plugin."""
        return asyncio.shield(self.sys_audio.restart())

    @api_process
    def reset(self, request: web.Request) -> Awaitable[None]:
        """Reset Audio plugin."""
        return asyncio.shield(self.sys_audio.reset())
