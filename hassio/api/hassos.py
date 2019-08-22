"""Init file for Hass.io HassOS RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable, Dict

import voluptuous as vol
from aiohttp import web

from ..const import (
    ATTR_BOARD,
    ATTR_VERSION,
    ATTR_VERSION_CLI,
    ATTR_VERSION_CLI_LATEST,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): vol.Coerce(str)})


class APIHassOS(CoreSysAttributes):
    """Handle RESTful API for HassOS functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return HassOS information."""
        return {
            ATTR_VERSION: self.sys_hassos.version,
            ATTR_VERSION_CLI: self.sys_hassos.version_cli,
            ATTR_VERSION_LATEST: self.sys_hassos.version_latest,
            ATTR_VERSION_CLI_LATEST: self.sys_hassos.version_cli_latest,
            ATTR_BOARD: self.sys_hassos.board,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update HassOS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_hassos.version_latest)

        await asyncio.shield(self.sys_hassos.update(version))

    @api_process
    async def update_cli(self, request: web.Request) -> None:
        """Update HassOS CLI."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_hassos.version_cli_latest)

        await asyncio.shield(self.sys_hassos.update_cli(version))

    @api_process
    def config_sync(self, request: web.Request) -> Awaitable[None]:
        """Trigger config reload on HassOS."""
        return asyncio.shield(self.sys_hassos.config_sync())
