"""Init file for Supervisor HassOS RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
import re
from typing import Any

from aiohttp import web
from awesomeversion import AwesomeVersion
import voluptuous as vol

from ..const import (
    ATTR_ACTIVITY_LED,
    ATTR_BLOCKED_REASON,
    ATTR_BOARD,
    ATTR_BOOT,
    ATTR_CURRENT_VERSION,
    ATTR_DEVICES,
    ATTR_DISK_LED,
    ATTR_HEARTBEAT_LED,
    ATTR_ID,
    ATTR_LATEST_VERSION,
    ATTR_NAME,
    ATTR_POWER_LED,
    ATTR_SERIAL,
    ATTR_SIZE,
    ATTR_STATE,
    ATTR_SWAP_SIZE,
    ATTR_SWAPPINESS,
    ATTR_UPDATE_AVAILABLE,
    ATTR_UPDATE_BLOCKED,
    ATTR_UPDATE_PENDING,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    ATTR_VERSION_PENDING,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APINotFound, BoardInvalidError
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..resolution.data import Issue
from ..validate import version_tag
from .const import (
    ATTR_BOOT_SLOT,
    ATTR_BOOT_SLOTS,
    ATTR_DATA_DISK,
    ATTR_DEV_PATH,
    ATTR_DEVICE,
    ATTR_DISKS,
    ATTR_KEYS,
    ATTR_MODEL,
    ATTR_STATUS,
    ATTR_SYSTEM_HEALTH_LED,
    ATTR_VENDOR,
    BootSlot,
)
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Raspberry Pi firmware management requires the io.hass.os.Boards.RaspberryPi
# .Firmware D-Bus interface first shipped in this OS Agent release.
RPI_FIRMWARE_MIN_OS_AGENT_VERSION: AwesomeVersion = AwesomeVersion("1.9.0")

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

# dropbear, which consumes authorized_keys on Home Assistant OS, ignores
# lines longer than 3000 bytes
SSH_AUTH_KEY_MAX_LENGTH = 3000

RE_SSH_KEY_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def ssh_auth_key(value: Any) -> str:
    """Run a basic sanity check on an SSH authorized key entry.

    Proper key validation is done by OS Agent; reject only what could write
    more than one authorized_keys line per key (control characters) or
    produce a line dropbear ignores (too long).
    """
    if not isinstance(value, str):
        raise vol.Invalid("SSH public key must be a string")

    key = value.strip()
    # dropbear and OS Agent limit the line length in bytes, not characters
    if not key or len(key.encode()) > SSH_AUTH_KEY_MAX_LENGTH:
        raise vol.Invalid("SSH public key is empty or too long")
    if RE_SSH_KEY_CONTROL_CHARS.search(key):
        raise vol.Invalid("SSH public key contains control characters")

    return key


SCHEMA_SSH_AUTHORIZED_KEYS = vol.Schema({vol.Required(ATTR_KEYS): [ssh_auth_key]})
# pylint: enable=no-value-for-parameter

# OS Agent validates submitted keys and treats clearing an already absent
# authorized_keys file as success since this release.
SSH_AUTH_KEYS_MIN_OS_AGENT_VERSION: AwesomeVersion = AwesomeVersion("1.10.0")


class APIOS(CoreSysAttributes):
    """Handle RESTful API for OS functions."""

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return OS information."""
        return {
            # Report an installed update pending activation as the current
            # version: the Core update entity compares version with
            # version_latest, so it would offer the update again otherwise.
            # Once Core consumes version_pending, this can be limited to Core
            # versions predating that support.
            ATTR_VERSION: self.sys_os.version_pending or self.sys_os.version,
            ATTR_VERSION_LATEST: self.sys_os.latest_version,
            ATTR_VERSION_PENDING: self.sys_os.version_pending,
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
    async def ssh_authorized_keys(self, request: web.Request) -> None:
        """Replace root's SSH authorized keys on the host."""
        if (
            not self.sys_dbus.agent.is_connected
            or self.sys_dbus.agent.version < SSH_AUTH_KEYS_MIN_OS_AGENT_VERSION
        ):
            raise APINotFound(
                f"OS Agent {SSH_AUTH_KEYS_MIN_OS_AGENT_VERSION} or newer required "
                "for SSH authorized keys management",
                _LOGGER.debug,
            )

        body = await api_validate(SCHEMA_SSH_AUTHORIZED_KEYS, request)
        await asyncio.shield(self.sys_os.set_ssh_authorized_keys(body[ATTR_KEYS]))

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

    def _check_rpi_firmware_available(self) -> None:
        """Reject the request unless Raspberry Pi firmware management is usable."""
        if (
            not self.sys_dbus.agent.is_connected
            or self.sys_dbus.agent.version < RPI_FIRMWARE_MIN_OS_AGENT_VERSION
        ):
            raise APINotFound(
                f"OS Agent {RPI_FIRMWARE_MIN_OS_AGENT_VERSION} or newer required "
                "for Raspberry Pi firmware management",
                _LOGGER.debug,
            )

        if not self.sys_dbus.agent.board.has_rpi_firmware:
            raise APINotFound(
                "Raspberry Pi firmware is not available on this board", _LOGGER.debug
            )

    @api_process
    async def boards_raspberrypi_firmware_info(
        self, request: web.Request
    ) -> dict[str, Any]:
        """Get Raspberry Pi firmware state."""
        self._check_rpi_firmware_available()
        rpi = self.sys_dbus.agent.board.rpi_firmware
        self._sync_rpi_firmware_blocked_issue(rpi.update_blocked)
        return {
            ATTR_CURRENT_VERSION: rpi.current_version,
            ATTR_LATEST_VERSION: rpi.latest_version,
            ATTR_UPDATE_AVAILABLE: rpi.update_available,
            ATTR_UPDATE_BLOCKED: rpi.update_blocked,
            ATTR_UPDATE_PENDING: rpi.update_pending,
            ATTR_BLOCKED_REASON: rpi.blocked_reason,
        }

    @api_process
    async def boards_raspberrypi_firmware_update(self, request: web.Request) -> None:
        """Trigger Raspberry Pi firmware (and VL805 where present) update."""
        self._check_rpi_firmware_available()

        # Reject early without scheduling the update job. The OS manager would
        # also reject it, but raising here keeps the resolution state in sync
        # without waiting for the next coordinator poll.
        if self.sys_dbus.agent.board.rpi_firmware.update_blocked:
            self._sync_rpi_firmware_blocked_issue(True)
            raise APIError(
                "Raspberry Pi firmware update is unavailable on this boot device",
                _LOGGER.warning,
            )

        await asyncio.shield(self.sys_os.update_raspberrypi_firmware())

    def _sync_rpi_firmware_blocked_issue(self, blocked: bool) -> None:
        """Create or dismiss the RPI_FIRMWARE_UPDATE_BLOCKED issue based on agent state."""
        issue = Issue(IssueType.RPI_FIRMWARE_UPDATE_BLOCKED, ContextType.SYSTEM)
        existing = self.sys_resolution.get_issue_if_present(issue)
        if blocked:
            if existing is None:
                self.sys_resolution.create_issue(
                    IssueType.RPI_FIRMWARE_UPDATE_BLOCKED, ContextType.SYSTEM
                )
        elif existing is not None:
            self.sys_resolution.dismiss_issue(existing)

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
