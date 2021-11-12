"""Init file for Supervisor Supervisor RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable

from aiohttp import web
import voluptuous as vol

from supervisor.resolution.const import ContextType, SuggestionType

from ..const import (
    ATTR_ADDONS,
    ATTR_ADDONS_REPOSITORIES,
    ATTR_ARCH,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_CHANNEL,
    ATTR_CONTENT_TRUST,
    ATTR_CPU_PERCENT,
    ATTR_DEBUG,
    ATTR_DEBUG_BLOCK,
    ATTR_DESCRIPTON,
    ATTR_DIAGNOSTICS,
    ATTR_FORCE_SECURITY,
    ATTR_HEALTHY,
    ATTR_ICON,
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
    ATTR_UPDATE_AVAILABLE,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    ATTR_WAIT_BOOT,
    CONTENT_TYPE_BINARY,
    LogLevel,
    UpdateChannel,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..utils.validate import validate_timezone
from ..validate import repositories, version_tag, wait_boot
from .const import (
    ATTR_AVAILABLE_UPDATES,
    ATTR_CHANGELOG_PATH,
    ATTR_CHANGELOG_URL,
    ATTR_PANEL_PATH,
    ATTR_UPDATE_PATH,
    ATTR_UPDATE_TYPE,
)
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_CHANNEL): vol.Coerce(UpdateChannel),
        vol.Optional(ATTR_ADDONS_REPOSITORIES): repositories,
        vol.Optional(ATTR_TIMEZONE): validate_timezone,
        vol.Optional(ATTR_WAIT_BOOT): wait_boot,
        vol.Optional(ATTR_LOGGING): vol.Coerce(LogLevel),
        vol.Optional(ATTR_DEBUG): vol.Boolean(),
        vol.Optional(ATTR_DEBUG_BLOCK): vol.Boolean(),
        vol.Optional(ATTR_DIAGNOSTICS): vol.Boolean(),
        vol.Optional(ATTR_CONTENT_TRUST): vol.Boolean(),
        vol.Optional(ATTR_FORCE_SECURITY): vol.Boolean(),
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
        list_addons = []
        for addon in self.sys_addons.installed:
            list_addons.append(
                {
                    ATTR_NAME: addon.name,
                    ATTR_SLUG: addon.slug,
                    ATTR_DESCRIPTON: addon.description,
                    ATTR_STATE: addon.state,
                    ATTR_VERSION: addon.version,
                    ATTR_VERSION_LATEST: addon.latest_version,
                    ATTR_UPDATE_AVAILABLE: addon.need_update,
                    ATTR_REPOSITORY: addon.repository,
                    ATTR_ICON: addon.with_icon,
                    ATTR_LOGO: addon.with_logo,
                }
            )

        return {
            ATTR_VERSION: self.sys_supervisor.version,
            ATTR_VERSION_LATEST: self.sys_supervisor.latest_version,
            ATTR_UPDATE_AVAILABLE: self.sys_supervisor.need_update,
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
            self.sys_dbus.agent.diagnostics = body[ATTR_DIAGNOSTICS]

        if ATTR_LOGGING in body:
            self.sys_config.logging = body[ATTR_LOGGING]

        # REMOVE: 2021.7
        if ATTR_CONTENT_TRUST in body:
            self.sys_security.content_trust = body[ATTR_CONTENT_TRUST]

        # REMOVE: 2021.7
        if ATTR_FORCE_SECURITY in body:
            self.sys_security.force = body[ATTR_FORCE_SECURITY]

        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            await asyncio.shield(self.sys_store.update_repositories(new))

            # Fix invalid repository
            found_invalid = False
            for suggestion in self.sys_resolution.suggestions:
                if (
                    suggestion.type != SuggestionType.EXECUTE_REMOVE
                    and suggestion.context != ContextType
                ):
                    continue
                found_invalid = True
                await self.sys_resolution.apply_suggestion(suggestion)

            if found_invalid:
                raise APIError("Invalid Add-on repository!")

        self.sys_updater.save_data()
        self.sys_config.save_data()

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
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload add-ons, configuration, etc."""
        return asyncio.shield(
            asyncio.wait(
                [
                    self.sys_updater.reload(),
                    self.sys_homeassistant.secrets.reload(),
                    self.sys_resolution.evaluate.evaluate_system(),
                ]
            )
        )

    @api_process
    def repair(self, request: web.Request) -> Awaitable[None]:
        """Try to repair the local setup / overlayfs."""
        return asyncio.shield(self.sys_core.repair())

    @api_process
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Soft restart Supervisor."""
        return asyncio.shield(self.sys_supervisor.restart())

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return supervisor Docker logs."""
        return self.sys_supervisor.logs()

    @api_process
    async def available_updates(self, request: web.Request) -> dict[str, Any]:
        """Return a list of items with available updates."""
        available_updates = []

        # Core
        if self.sys_homeassistant.need_update:
            available_updates.append(
                {
                    ATTR_UPDATE_TYPE: "core",
                    ATTR_UPDATE_PATH: "/core/update",
                    ATTR_PANEL_PATH: "/update-available/core",
                    ATTR_CHANGELOG_URL: "https://www.home-assistant.io/latest-release-notes/",
                    ATTR_VERSION: self.sys_homeassistant.version,
                    ATTR_VERSION_LATEST: self.sys_homeassistant.latest_version,
                }
            )

        # Supervisor
        if self.sys_supervisor.need_update:
            available_updates.append(
                {
                    ATTR_UPDATE_TYPE: "supervisor",
                    ATTR_UPDATE_PATH: "/supervisor/update",
                    ATTR_PANEL_PATH: "/update-available/supervisor",
                    ATTR_CHANGELOG_URL: f"https://github.com/home-assistant/supervisor/compare/{self.sys_supervisor.version}...{self.sys_supervisor.latest_version}",
                    ATTR_VERSION: self.sys_supervisor.version,
                    ATTR_VERSION_LATEST: self.sys_supervisor.latest_version,
                }
            )

        # OS
        if self.sys_os.need_update:
            available_updates.append(
                {
                    ATTR_UPDATE_TYPE: "os",
                    ATTR_UPDATE_PATH: "/os/update",
                    ATTR_PANEL_PATH: "/update-available/os",
                    ATTR_CHANGELOG_URL: f"https://github.com/home-assistant/operating-system/compare/{self.sys_os.version}...{self.sys_os.latest_version}",
                    ATTR_VERSION: self.sys_os.version,
                    ATTR_VERSION_LATEST: self.sys_os.latest_version,
                }
            )

        # Add-ons
        available_updates.extend(
            {
                ATTR_UPDATE_TYPE: "addon",
                ATTR_NAME: addon.name,
                ATTR_ICON: f"/addons/{addon.slug}/icon" if addon.with_icon else None,
                ATTR_CHANGELOG_PATH: f"/addons/{addon.slug}/changelog"
                if addon.with_changelog
                else None,
                ATTR_UPDATE_PATH: f"/addons/{addon.slug}/update",
                ATTR_PANEL_PATH: f"/update-available/{addon.slug}",
                ATTR_VERSION: addon.version,
                ATTR_VERSION_LATEST: addon.latest_version,
            }
            for addon in self.sys_addons.installed
            if addon.need_update
        )

        return {ATTR_AVAILABLE_UPDATES: available_updates}
