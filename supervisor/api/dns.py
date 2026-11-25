"""Init file for Supervisor DNS RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import ATTR_HOST, ATTR_LOCALS, ATTR_SERVERS
from ..plugins.dns import PluginDns
from ..validate import dns_server_list
from .const import ATTR_FALLBACK, ATTR_LLMNR, ATTR_MDNS
from .plugins import APIPlugin
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_SERVERS): dns_server_list,
        vol.Optional(ATTR_FALLBACK): vol.Boolean(),
    }
)


class APICoreDNS(APIPlugin[PluginDns]):
    """Handle RESTful API for DNS functions."""

    def _info(self) -> dict[str, Any]:
        """Return DNS information."""
        return super()._info() | {
            ATTR_HOST: str(self.sys_docker.network.dns),
            ATTR_SERVERS: self.plugin.servers,
            ATTR_LOCALS: self.plugin.locals,
            ATTR_MDNS: self.plugin.mdns,
            ATTR_LLMNR: self.plugin.llmnr,
            ATTR_FALLBACK: self.plugin.fallback,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set DNS options."""
        body = await api_validate(SCHEMA_OPTIONS, request)
        restart_required = False

        if ATTR_SERVERS in body:
            self.plugin.servers = body[ATTR_SERVERS]
            restart_required = True

        if ATTR_FALLBACK in body:
            self.plugin.fallback = body[ATTR_FALLBACK]
            restart_required = True

        if restart_required:
            self.sys_create_task(self.plugin.restart())

        await self.plugin.save_data()

    @api_process
    def reset(self, request: web.Request) -> Awaitable[None]:
        """Reset CoreDNS plugin."""
        return asyncio.shield(self.plugin.reset())
