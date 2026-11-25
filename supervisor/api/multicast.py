"""Init file for Supervisor Multicast RESTful API."""

import asyncio
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import ATTR_ENABLED
from ..plugins.multicast import PluginMulticast
from .plugins import APIPlugin
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({vol.Optional(ATTR_ENABLED): vol.Boolean()})


class APIMulticast(APIPlugin[PluginMulticast]):
    """Handle RESTful API for Multicast functions."""

    def _info(self) -> dict[str, Any]:
        """Return Multicast information."""
        return super()._info() | {
            ATTR_ENABLED: self.plugin.enabled,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set Multicast options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_ENABLED in body:
            if body[ATTR_ENABLED]:
                await asyncio.shield(self.plugin.enable())
            else:
                await asyncio.shield(self.plugin.disable())
