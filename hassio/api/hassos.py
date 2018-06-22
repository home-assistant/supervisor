"""Init file for Hass.io hassos rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import ATTR_VERSION, ATTR_BOARD
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHassOS(CoreSysAttributes):
    """Handle rest api for hassos functions."""

    @api_process
    async def info(self, request):
        """Return hassos information."""
        return {
            ATTR_VERSION: self.sys_hassos.version,
            ATTR_BOARD: self.sys_hassos.board,
        }

    @api_process
    def config_sync(self, request):
        """Trigger config reload on HassOS."""
        return asyncio.shield(self.sys_hassos.config_sync())
