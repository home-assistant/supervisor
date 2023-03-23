"""Init file for Supervisor HassOS RESTful API."""
import asyncio
from collections.abc import Awaitable
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_BOARD,
    ATTR_BOOT,
    ATTR_DEVICES,
    ATTR_ID,
    ATTR_NAME,
    ATTR_SERIAL,
    ATTR_SIZE,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from ..exceptions import BoardInvalidError
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..validate import version_tag
from .const import (
    ATTR_DATA_DISK,
    ATTR_DEV_PATH,
    ATTR_DEVICE,
    ATTR_DISK_LED,
    ATTR_DISKS,
    ATTR_HEARTBEAT_LED,
    ATTR_MODEL,
    ATTR_POWER_LED,
    ATTR_VENDOR,
)
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})
SCHEMA_DISK = vol.Schema({vol.Required(ATTR_DEVICE): str})

# pylint: disable=no-value-for-parameter
SCHEMA_YELLOW_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_DISK_LED): vol.Boolean(),
        vol.Optional(ATTR_HEARTBEAT_LED): vol.Boolean(),
        vol.Optional(ATTR_POWER_LED): vol.Boolean(),
    }
)


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
            ATTR_DATA_DISK: self.sys_os.datadisk.disk_used.id,
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
            ATTR_DEVICES: [disk.id for disk in self.sys_os.datadisk.available_disks],
            ATTR_DISKS: [
                {
                    ATTR_NAME: disk.name,
                    ATTR_VENDOR: disk.vendor,
                    ATTR_MODEL: disk.model,
                    ATTR_SERIAL: disk.serial,
                    ATTR_SIZE: disk.size,
                    ATTR_ID: disk.id,
                    ATTR_DEV_PATH: disk.device_path.as_posix(),
                }
                for disk in self.sys_os.datadisk.available_disks
            ],
        }

    @api_process
    async def boards_yellow_info(self, request: web.Request) -> dict[str, Any]:
        """Get yellow board settings."""
        return {
            ATTR_DISK_LED: self.sys_dbus.agent.board.yellow.disk_led,
            ATTR_HEARTBEAT_LED: self.sys_dbus.agent.board.yellow.heartbeat_led,
            ATTR_POWER_LED: self.sys_dbus.agent.board.yellow.power_led,
        }

    @api_process
    async def boards_yellow_options(self, request: web.Request) -> None:
        """Update yellow board settings."""
        body = await api_validate(SCHEMA_YELLOW_OPTIONS, request)

        if ATTR_DISK_LED in body:
            self.sys_dbus.agent.board.yellow.disk_led = body[ATTR_DISK_LED]

        if ATTR_HEARTBEAT_LED in body:
            self.sys_dbus.agent.board.yellow.heartbeat_led = body[ATTR_HEARTBEAT_LED]

        if ATTR_POWER_LED in body:
            self.sys_dbus.agent.board.yellow.power_led = body[ATTR_POWER_LED]

        self.sys_resolution.create_issue(
            IssueType.REBOOT_REQUIRED,
            ContextType.SYSTEM,
            suggestions=[SuggestionType.EXECUTE_REBOOT],
        )

    @api_process
    async def boards_other_info(self, request: web.Request) -> dict[str, Any]:
        """Empty success return if board is in use, error otherwise."""
        if request.match_info["board"] != self.sys_os.board:
            raise BoardInvalidError(
                f"{request.match_info['board']} board is not in use", _LOGGER.error
            )

        return {}
