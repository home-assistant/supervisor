"""Init file for Supervisor Supervisor RESTful API."""

import asyncio
from collections.abc import Awaitable
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ADDONS,
    ATTR_ADDONS_REPOSITORIES,
    ATTR_ARCH,
    ATTR_AUTO_UPDATE,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_CHANNEL,
    ATTR_CONTENT_TRUST,
    ATTR_COUNTRY,
    ATTR_CPU_PERCENT,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DETECT_BLOCKING_IO,
    ATTR_DIAGNOSTICS,
    ATTR_FORCE_SECURITY,
    ATTR_HEALTHY,
    ATTR_ICON,
    ATTR_IP_ADDRESS,
    ATTR_LOGGING,
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
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    ATTR_WAIT_BOOT,
    LogLevel,
    UpdateChannel,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..store.validate import repositories
from ..utils.blockbuster import BlockBusterManager
from ..utils.sentry import close_sentry, init_sentry
from ..utils.validate import validate_timezone
from ..validate import version_tag, wait_boot
from .const import CONTENT_TYPE_TEXT, DetectBlockingIO
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_CHANNEL): vol.Coerce(UpdateChannel),
        vol.Optional(ATTR_ADDONS_REPOSITORIES): repositories,
        vol.Optional(ATTR_TIMEZONE): str,
        vol.Optional(ATTR_WAIT_BOOT): wait_boot,
        vol.Optional(ATTR_LOGGING): vol.Coerce(LogLevel),
        vol.Optional(ATTR_DEBUG): vol.Boolean(),
        vol.Optional(ATTR_DEBUG_BLOCK): vol.Boolean(),
        vol.Optional(ATTR_DIAGNOSTICS): vol.Boolean(),
        vol.Optional(ATTR_CONTENT_TRUST): vol.Boolean(),
        vol.Optional(ATTR_FORCE_SECURITY): vol.Boolean(),
        vol.Optional(ATTR_AUTO_UPDATE): vol.Boolean(),
        vol.Optional(ATTR_DETECT_BLOCKING_IO): vol.Coerce(DetectBlockingIO),
        vol.Optional(ATTR_COUNTRY): str,
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
    async def info(self, request: web.Request) -> dict[str, Any]:
        """Return host information."""
        return {
            ATTR_VERSION: self.sys_supervisor.version,
            ATTR_VERSION_LATEST: self.sys_supervisor.latest_version,
            ATTR_UPDATE_AVAILABLE: self.sys_supervisor.need_update,
            ATTR_CHANNEL: self.sys_updater.channel,
            ATTR_ARCH: self.sys_supervisor.arch,
            ATTR_SUPPORTED: self.sys_core.supported,
            ATTR_HEALTHY: self.sys_core.healthy,
            ATTR_IP_ADDRESS: str(self.sys_supervisor.ip_address),
            ATTR_TIMEZONE: self.sys_config.timezone,
            ATTR_LOGGING: self.sys_config.logging,
            ATTR_DEBUG: self.sys_config.debug,
            ATTR_DEBUG_BLOCK: self.sys_config.debug_block,
            ATTR_DIAGNOSTICS: self.sys_config.diagnostics,
            ATTR_AUTO_UPDATE: self.sys_updater.auto_update,
            ATTR_DETECT_BLOCKING_IO: BlockBusterManager.is_enabled(),
            ATTR_COUNTRY: self.sys_config.country,
            # Depricated
            ATTR_WAIT_BOOT: self.sys_config.wait_boot,
            ATTR_ADDONS: [
                {
                    ATTR_NAME: addon.name,
                    ATTR_SLUG: addon.slug,
                    ATTR_VERSION: addon.version,
                    ATTR_VERSION_LATEST: addon.latest_version,
                    ATTR_UPDATE_AVAILABLE: addon.need_update,
                    ATTR_STATE: addon.state,
                    ATTR_REPOSITORY: addon.repository,
                    ATTR_ICON: addon.with_icon,
                }
                for addon in self.sys_addons.local.values()
            ],
            ATTR_ADDONS_REPOSITORIES: [
                {ATTR_NAME: store.name, ATTR_SLUG: store.slug}
                for store in self.sys_store.all
            ],
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set Supervisor options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        # Timezone must be first as validation is incomplete
        # If a timezone is present we do that validation after in the executor
        if (
            ATTR_TIMEZONE in body
            and (timezone := body[ATTR_TIMEZONE]) != self.sys_config.timezone
        ):
            await self.sys_run_in_executor(validate_timezone, timezone)
            await self.sys_config.set_timezone(timezone)

        if ATTR_CHANNEL in body:
            self.sys_updater.channel = body[ATTR_CHANNEL]

        if ATTR_COUNTRY in body:
            self.sys_config.country = body[ATTR_COUNTRY]

        if ATTR_DEBUG in body:
            self.sys_config.debug = body[ATTR_DEBUG]

        if ATTR_DEBUG_BLOCK in body:
            self.sys_config.debug_block = body[ATTR_DEBUG_BLOCK]

        if ATTR_DIAGNOSTICS in body:
            self.sys_config.diagnostics = body[ATTR_DIAGNOSTICS]
            await self.sys_dbus.agent.set_diagnostics(body[ATTR_DIAGNOSTICS])

            if body[ATTR_DIAGNOSTICS]:
                init_sentry(self.coresys)
            else:
                close_sentry()

        if ATTR_LOGGING in body:
            self.sys_config.logging = body[ATTR_LOGGING]

        if ATTR_AUTO_UPDATE in body:
            self.sys_updater.auto_update = body[ATTR_AUTO_UPDATE]

        if detect_blocking_io := body.get(ATTR_DETECT_BLOCKING_IO):
            if detect_blocking_io == DetectBlockingIO.ON_AT_STARTUP:
                self.sys_config.detect_blocking_io = True
                detect_blocking_io = DetectBlockingIO.ON

            if detect_blocking_io == DetectBlockingIO.ON:
                BlockBusterManager.activate()
            elif detect_blocking_io == DetectBlockingIO.OFF:
                self.sys_config.detect_blocking_io = False
                BlockBusterManager.deactivate()

        # Deprecated
        if ATTR_WAIT_BOOT in body:
            self.sys_config.wait_boot = body[ATTR_WAIT_BOOT]

        # Save changes before processing addons in case of errors
        await self.sys_updater.save_data()
        await self.sys_config.save_data()

        # Remove: 2022.9
        if ATTR_ADDONS_REPOSITORIES in body:
            await asyncio.shield(
                self.sys_store.update_repositories(set(body[ATTR_ADDONS_REPOSITORIES]))
            )

        await self.sys_resolution.evaluate.evaluate_system()

    @api_process
    async def stats(self, request: web.Request) -> dict[str, Any]:
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

        # This option is useless outside of DEV
        if not self.sys_dev and not self.sys_supervisor.need_update:
            raise APIError(
                f"No supervisor update available - {self.sys_supervisor.version!s}"
            )

        if self.sys_dev:
            version = body.get(ATTR_VERSION, self.sys_updater.version_supervisor)
        else:
            version = self.sys_updater.version_supervisor

        await asyncio.shield(self.sys_supervisor.update(version))

    @api_process
    async def reload(self, request: web.Request) -> None:
        """Reload add-ons, configuration, etc."""
        await asyncio.gather(
            asyncio.shield(self.sys_updater.reload()),
            asyncio.shield(self.sys_homeassistant.secrets.reload()),
            asyncio.shield(self.sys_resolution.evaluate.evaluate_system()),
        )

    @api_process
    def repair(self, request: web.Request) -> Awaitable[None]:
        """Try to repair the local setup / overlayfs."""
        return asyncio.shield(self.sys_core.repair())

    @api_process
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Soft restart Supervisor."""
        return asyncio.shield(self.sys_supervisor.restart())

    @api_process_raw(CONTENT_TYPE_TEXT, error_type=CONTENT_TYPE_TEXT)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return supervisor Docker logs."""
        return self.sys_supervisor.logs()
