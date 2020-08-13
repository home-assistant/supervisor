"""Init file for Supervisor Supervisor RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ADDONS,
    ATTR_ADDONS_REPOSITORIES,
    ATTR_ARCH,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_CHANNEL,
    ATTR_CPU_PERCENT,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DESCRIPTON,
    ATTR_DIAGNOSTICS,
    ATTR_HEALTHY,
    ATTR_ICON,
    ATTR_INSTALLED,
    ATTR_IP_ADDRESS,
    ATTR_LOGGING,
    ATTR_LOGO,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_PERCENT,
    ATTR_MEMORY_USAGE,
    ATTR_NAME,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_REPOSITORY,
    ATTR_SLUG,
    ATTR_STATE,
    ATTR_SUPPORTED,
    ATTR_TIMEZONE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    ATTR_WAIT_BOOT,
    CONTENT_TYPE_BINARY,
    SUPERVISOR_VERSION,
    LogLevel,
    UpdateChannels,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..utils.validate import validate_timezone
from ..validate import repositories, version_tag, wait_boot
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_CHANNEL): vol.Coerce(UpdateChannels),
        vol.Optional(ATTR_ADDONS_REPOSITORIES): repositories,
        vol.Optional(ATTR_TIMEZONE): validate_timezone,
        vol.Optional(ATTR_WAIT_BOOT): wait_boot,
        vol.Optional(ATTR_LOGGING): vol.Coerce(LogLevel),
        vol.Optional(ATTR_DEBUG): vol.Boolean(),
        vol.Optional(ATTR_DEBUG_BLOCK): vol.Boolean(),
        vol.Optional(ATTR_DIAGNOSTICS): vol.Boolean(),
    }
)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): version_tag})


class APISupervisor(CoreSysAttributes):
    """Handle RESTful API for Supervisor functions."""

    @api_process
    async def ping(self, request):
        """Return ok for signal that the API is ready."""
        return True

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return host information."""
        list_addons = []
        for addon in self.sys_addons.installed:
            list_addons.append(
                {
                    ATTR_NAME: addon.name,
                    ATTR_SLUG: addon.slug,
                    ATTR_DESCRIPTON: addon.description,
                    ATTR_STATE: await addon.state(),
                    ATTR_VERSION: addon.latest_version,
                    ATTR_INSTALLED: addon.version,
                    ATTR_REPOSITORY: addon.repository,
                    ATTR_ICON: addon.with_icon,
                    ATTR_LOGO: addon.with_logo,
                }
            )

        return {
            ATTR_VERSION: SUPERVISOR_VERSION,
            ATTR_VERSION_LATEST: self.sys_updater.version_supervisor,
            ATTR_CHANNEL: self.sys_updater.channel,
            ATTR_ARCH: self.sys_supervisor.arch,
            ATTR_SUPPORTED: self.sys_core.supported,
            ATTR_HEALTHY: self.sys_core.healthy,
            ATTR_IP_ADDRESS: str(self.sys_supervisor.ip_address),
            ATTR_WAIT_BOOT: self.sys_config.wait_boot,
            ATTR_TIMEZONE: self.sys_config.timezone,
            ATTR_LOGGING: self.sys_config.logging,
            ATTR_DEBUG: self.sys_config.debug,
            ATTR_DEBUG_BLOCK: self.sys_config.debug_block,
            ATTR_DIAGNOSTICS: self.sys_config.diagnostics,
            ATTR_ADDONS: list_addons,
            ATTR_ADDONS_REPOSITORIES: self.sys_config.addons_repositories,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set Supervisor options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_CHANNEL in body:
            self.sys_updater.channel = body[ATTR_CHANNEL]

        if ATTR_TIMEZONE in body:
            self.sys_config.timezone = body[ATTR_TIMEZONE]

        if ATTR_WAIT_BOOT in body:
            self.sys_config.wait_boot = body[ATTR_WAIT_BOOT]

        if ATTR_DEBUG in body:
            self.sys_config.debug = body[ATTR_DEBUG]

        if ATTR_DEBUG_BLOCK in body:
            self.sys_config.debug_block = body[ATTR_DEBUG_BLOCK]

        if ATTR_DIAGNOSTICS in body:
            self.sys_config.diagnostics = body[ATTR_DIAGNOSTICS]

        if ATTR_LOGGING in body:
            self.sys_config.logging = body[ATTR_LOGGING]

        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            await asyncio.shield(self.sys_store.update_repositories(new))

        self.sys_updater.save_data()
        self.sys_config.save_data()

    @api_process
    async def stats(self, request: web.Request) -> Dict[str, Any]:
        """Return resource information."""
        stats = await self.sys_supervisor.stats()

        return {
            ATTR_CPU_PERCENT: stats.cpu_percent,
            ATTR_MEMORY_USAGE: stats.memory_usage,
            ATTR_MEMORY_LIMIT: stats.memory_limit,
            ATTR_MEMORY_PERCENT: stats.memory_percent,
            ATTR_NETWORK_RX: stats.network_rx,
            ATTR_NETWORK_TX: stats.network_tx,
            ATTR_BLK_READ: stats.blk_read,
            ATTR_BLK_WRITE: stats.blk_write,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update Supervisor OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_updater.version_supervisor)

        if version == self.sys_supervisor.version:
            raise APIError(f"Version {version} is already in use")
        await asyncio.shield(self.sys_supervisor.update(version))

    @api_process
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload add-ons, configuration, etc."""
        return asyncio.shield(
            asyncio.wait([self.sys_updater.reload(), self.sys_secrets.reload()])
        )

    @api_process
    def repair(self, request: web.Request) -> Awaitable[None]:
        """Try to repair the local setup / overlayfs."""
        return asyncio.shield(self.sys_core.repair())

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return supervisor Docker logs."""
        return self.sys_supervisor.logs()
