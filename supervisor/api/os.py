"""Init file for Supervisor HassOS RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
import re
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ACTIVITY_LED,
    ATTR_BOARD,
    ATTR_BOOT,
    ATTR_DEVICES,
    ATTR_DISK_LED,
    ATTR_HEARTBEAT_LED,
    ATTR_ID,
    ATTR_NAME,
    ATTR_POWER_LED,
    ATTR_SERIAL,
    ATTR_SIZE,
    ATTR_STATE,
    ATTR_SWAP_SIZE,
    ATTR_SWAPPINESS,
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APINotFound, BoardInvalidError
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..validate import version_tag
from .const import (
    ATTR_BOOT_SLOT,
    ATTR_BOOT_SLOTS,
    ATTR_DATA_DISK,
    ATTR_DEV_PATH,
    ATTR_DEVICE,
    ATTR_DISKS,
    ATTR_MODEL,
    ATTR_STATUS,
    ATTR_SYSTEM_HEALTH_LED,
    ATTR_VENDOR,
    BootSlot,
)
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})
SCHEMA_SET_BOOT_SLOT = vol.Schema({vol.Required(ATTR_BOOT_SLOT): vol.Coerce(BootSlot)})
SCHEMA_DISK = vol.Schema({vol.Required(ATTR_DEVICE): str})

SCHEMA_YELLOW_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_DISK_LED): vol.Boolean(),
        vol.Optional(ATTR_HEARTBEAT_LED): vol.Boolean(),
        vol.Optional(ATTR_POWER_LED): vol.Boolean(),
    }
)
SCHEMA_GREEN_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_ACTIVITY_LED): vol.Boolean(),
        vol.Optional(ATTR_POWER_LED): vol.Boolean(),
        vol.Optional(ATTR_SYSTEM_HEALTH_LED): vol.Boolean(),
    }
)

RE_SWAP_SIZE = re.compile(r"^\d+([KMG](i?B)?|B)?$", re.IGNORECASE)

SCHEMA_SWAP_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_SWAP_SIZE): vol.Match(RE_SWAP_SIZE),
        vol.Optional(ATTR_SWAPPINESS): vol.All(int, vol.Range(min=0, max=200)),
    }
)
# pylint: enable=no-value-for-parameter


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
            ATTR_DATA_DISK: self.sys_os.datadisk.disk_used_id,
            ATTR_BOOT_SLOTS: {
                slot.bootname: {
                    ATTR_STATE: slot.state,
                    ATTR_STATUS: slot.boot_status,
                    ATTR_VERSION: slot.bundle_version,
                }
                for slot in self.sys_os.slots
                if slot.bootname
            },
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
    def wipe_data(self, request: web.Request) -> Awaitable[None]:
        """Trigger data disk wipe on Host."""
        return asyncio.shield(self.sys_os.datadisk.wipe_disk())

    @api_process
    async def set_boot_slot(self, request: web.Request) -> None:
        """Change the active boot slot and reboot into it."""
        body = await api_validate(SCHEMA_SET_BOOT_SLOT, request)
        await asyncio.shield(self.sys_os.set_boot_slot(body[ATTR_BOOT_SLOT]))

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
    async def boards_green_info(self, request: web.Request) -> dict[str, Any]:
        """Get green board settings."""
        return {
            ATTR_ACTIVITY_LED: self.sys_dbus.agent.board.green.activity_led,
            ATTR_POWER_LED: self.sys_dbus.agent.board.green.power_led,
            ATTR_SYSTEM_HEALTH_LED: self.sys_dbus.agent.board.green.user_led,
        }

    @api_process
    async def boards_green_options(self, request: web.Request) -> None:
        """Update green board settings."""
        body = await api_validate(SCHEMA_GREEN_OPTIONS, request)

        if ATTR_ACTIVITY_LED in body:
            await self.sys_dbus.agent.board.green.set_activity_led(
                body[ATTR_ACTIVITY_LED]
            )

        if ATTR_POWER_LED in body:
            await self.sys_dbus.agent.board.green.set_power_led(body[ATTR_POWER_LED])

        if ATTR_SYSTEM_HEALTH_LED in body:
            await self.sys_dbus.agent.board.green.set_user_led(
                body[ATTR_SYSTEM_HEALTH_LED]
            )

        await self.sys_dbus.agent.board.green.save_data()

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
            await self.sys_dbus.agent.board.yellow.set_disk_led(body[ATTR_DISK_LED])

        if ATTR_HEARTBEAT_LED in body:
            await self.sys_dbus.agent.board.yellow.set_heartbeat_led(
                body[ATTR_HEARTBEAT_LED]
            )

        if ATTR_POWER_LED in body:
            await self.sys_dbus.agent.board.yellow.set_power_led(body[ATTR_POWER_LED])

        await self.sys_dbus.agent.board.yellow.save_data()
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

    @api_process
    async def config_swap_info(self, request: web.Request) -> dict[str, Any]:
        """Get swap settings."""
        if (
            not self.coresys.os.available
            or not self.coresys.os.version
            or self.coresys.os.version < "15.0"
        ):
            raise APINotFound(
                "Home Assistant OS 15.0 or newer required for swap settings"
            )

        return {
            ATTR_SWAP_SIZE: self.sys_dbus.agent.swap.swap_size,
            ATTR_SWAPPINESS: self.sys_dbus.agent.swap.swappiness,
        }

    @api_process
    async def config_swap_options(self, request: web.Request) -> None:
        """Update swap settings."""
        if (
            not self.coresys.os.available
            or not self.coresys.os.version
            or self.coresys.os.version < "15.0"
        ):
            raise APINotFound(
                "Home Assistant OS 15.0 or newer required for swap settings"
            )

        body = await api_validate(SCHEMA_SWAP_OPTIONS, request)

        reboot_required = False

        if ATTR_SWAP_SIZE in body:
            old_size = self.sys_dbus.agent.swap.swap_size
            await self.sys_dbus.agent.swap.set_swap_size(body[ATTR_SWAP_SIZE])
            reboot_required = reboot_required or old_size != body[ATTR_SWAP_SIZE]

        if ATTR_SWAPPINESS in body:
            old_swappiness = self.sys_dbus.agent.swap.swappiness
            await self.sys_dbus.agent.swap.set_swappiness(body[ATTR_SWAPPINESS])
            reboot_required = reboot_required or old_swappiness != body[ATTR_SWAPPINESS]

        if reboot_required:
            self.sys_resolution.create_issue(
                IssueType.REBOOT_REQUIRED,
                ContextType.SYSTEM,
                suggestions=[SuggestionType.EXECUTE_REBOOT],
            )
