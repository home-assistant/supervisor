"""Init file for Supervisor DNS RESTful API."""
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
    ATTR_LOCALS,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_PERCENT,
    ATTR_MEMORY_USAGE,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_SERVERS,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    CONTENT_TYPE_BINARY,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..validate import dns_server_list, version_tag
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({vol.Optional(ATTR_SERVERS): dns_server_list})

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})


class APICoreDNS(CoreSysAttributes):
    """Handle RESTful API for DNS functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return DNS information."""
        return {
            ATTR_VERSION: self.sys_plugins.dns.version,
            ATTR_VERSION_LATEST: self.sys_plugins.dns.latest_version,
            ATTR_HOST: str(self.sys_docker.network.dns),
            ATTR_SERVERS: self.sys_plugins.dns.servers,
            ATTR_LOCALS: self.sys_host.network.dns_servers,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set DNS options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_SERVERS in body:
            self.sys_plugins.dns.servers = body[ATTR_SERVERS]
            self.sys_create_task(self.sys_plugins.dns.restart())

        self.sys_plugins.dns.save_data()

    @api_process
    async def stats(self, request: web.Request) -> Dict[str, Any]:
        """Return resource information."""
        stats = await self.sys_plugins.dns.stats()

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
        """Update DNS plugin."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_plugins.dns.latest_version)

        if version == self.sys_plugins.dns.version:
            raise APIError(f"Version {version} is already in use")
        await asyncio.shield(self.sys_plugins.dns.update(version))

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return DNS Docker logs."""
        return self.sys_plugins.dns.logs()

    @api_process
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Restart CoreDNS plugin."""
        return asyncio.shield(self.sys_plugins.dns.restart())

    @api_process
    def reset(self, request: web.Request) -> Awaitable[None]:
        """Reset CoreDNS plugin."""
        return asyncio.shield(self.sys_plugins.dns.reset())
