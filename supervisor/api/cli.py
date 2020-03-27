"""Init file for Supervisor HA cli RESTful API."""
import asyncio
import logging
from typing import Any, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): vol.Coerce(str)})


class APICli(CoreSysAttributes):
    """Handle RESTful API for HA Cli functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return HA cli information."""
        return {
            ATTR_VERSION: self.sys_cli.version,
            ATTR_VERSION_LATEST: self.sys_cli.latest_version,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update HA CLI."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_cli.latest_version)

        await asyncio.shield(self.sys_cli.update(version))
