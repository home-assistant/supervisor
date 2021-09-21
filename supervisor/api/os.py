"""Init file for Supervisor HassOS RESTful API."""
import asyncio
import logging
from pathlib import Path
from typing import Any, Awaitable

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_BOARD,
    ATTR_BOOT,
    ATTR_DEVICES,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from ..validate import version_tag
from .const import ATTR_DEVICE, ATTR_DISK_DATA
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})
SCHEMA_DISK = vol.Schema({vol.Required(ATTR_DEVICE): vol.All(str, vol.Coerce(Path))})


class APIOS(CoreSysAttributes):
    """Handle RESTful API for OS functions."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return OS information."""
        return {
            ATTR_VERSION: self.sys_os.version,
            ATTR_VERSION_LATEST: self.sys_os.latest_version,
            ATTR_UPDATE_AVAILABLE: self.sys_os.need_update,
            ATTR_BOARD: self.sys_os.board,
            ATTR_BOOT: self.sys_dbus.rauc.boot_slot,
            ATTR_DISK_DATA: self.sys_os.datadisk.disk_used,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_os.latest_version)

        await asyncio.shield(self.sys_os.update(version))

    @api_process
    def config_sync(self, request: web.Request) -> Awaitable[None]:
        """Trigger config reload on OS."""
        return asyncio.shield(self.sys_os.config_sync())

    @api_process
    async def migrate_data(self, request: web.Request) -> None:
        """Trigger data disk migration on Host."""
        body = await api_validate(SCHEMA_DISK, request)

        await asyncio.shield(self.sys_os.datadisk.migrate_disk(body[ATTR_DEVICE]))

    @api_process
    async def list_data(self, request: web.Request) -> dict[str, Any]:
        """Return possible data targets."""
        return {
            ATTR_DEVICES: self.sys_os.datadisk.available_disks,
        }
