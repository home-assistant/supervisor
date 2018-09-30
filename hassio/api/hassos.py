"""Init file for Hass.io HassOS RESTful API."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_BOARD, ATTR_VERSION_LATEST, ATTR_VERSION_CLI,
    ATTR_VERSION_CLI_LATEST)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHassOS(CoreSysAttributes):
    """Handle RESTful API for HassOS functions."""

    @api_process
    async def info(self, request):
        """Return HassOS information."""
        return {
            ATTR_VERSION: self.sys_hassos.version,
            ATTR_VERSION_CLI: self.sys_hassos.version_cli,
            ATTR_VERSION_LATEST: self.sys_hassos.version_latest,
            ATTR_VERSION_CLI_LATEST: self.sys_hassos.version_cli_latest,
            ATTR_BOARD: self.sys_hassos.board,
        }

    @api_process
    async def update(self, request):
        """Update HassOS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_hassos.version_latest)

        await asyncio.shield(self.sys_hassos.update(version))

    @api_process
    async def update_cli(self, request):
        """Update HassOS CLI."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_hassos.version_cli_latest)

        await asyncio.shield(self.sys_hassos.update_cli(version))

    @api_process
    def config_sync(self, request):
        """Trigger config reload on HassOS."""
        return asyncio.shield(self.sys_hassos.config_sync())
