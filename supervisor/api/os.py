"""Init file for Supervisor HassOS RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_BOARD,
    ATTR_BOOT,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from ..validate import version_tag
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})


class APIOS(CoreSysAttributes):
    """Handle RESTful API for OS functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return OS information."""
        return {
            ATTR_VERSION: self.sys_hassos.version,
            ATTR_VERSION_LATEST: self.sys_hassos.latest_version,
            ATTR_UPDATE_AVAILABLE: self.sys_hassos.need_update,
            ATTR_BOARD: self.sys_hassos.board,
            ATTR_BOOT: self.sys_dbus.rauc.boot_slot,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_hassos.latest_version)

        await asyncio.shield(self.sys_hassos.update(version))

    @api_process
    async def config_sync(self, request: web.Request) -> Awaitable[None]:
        """Trigger config reload on OS."""
        await asyncio.shield(self.sys_hassos.config_sync())
