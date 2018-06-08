"""Init file for HassIO supervisor rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_ADDONS, ATTR_VERSION, ATTR_LAST_VERSION, ATTR_CHANNEL, ATTR_ARCH,
    HASSIO_VERSION, ATTR_ADDONS_REPOSITORIES, ATTR_LOGO, ATTR_REPOSITORY,
    ATTR_DESCRIPTON, ATTR_NAME, ATTR_SLUG, ATTR_INSTALLED, ATTR_TIMEZONE,
    ATTR_STATE, ATTR_WAIT_BOOT, ATTR_CPU_PERCENT, ATTR_MEMORY_USAGE,
    ATTR_MEMORY_LIMIT, ATTR_NETWORK_RX, ATTR_NETWORK_TX, ATTR_BLK_READ,
    ATTR_BLK_WRITE, CONTENT_TYPE_BINARY, ATTR_ICON)
from ..coresys import CoreSysAttributes
from ..validate import validate_timezone, WAIT_BOOT, REPOSITORIES, CHANNELS

_LOGGER = logging.getLogger(__name__)

SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_CHANNEL): CHANNELS,
    vol.Optional(ATTR_ADDONS_REPOSITORIES): REPOSITORIES,
    vol.Optional(ATTR_TIMEZONE): validate_timezone,
    vol.Optional(ATTR_WAIT_BOOT): WAIT_BOOT,
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APISupervisor(CoreSysAttributes):
    """Handle rest api for supervisor functions."""

    @api_process
    async def ping(self, request):
        """Return ok for signal that the api is ready."""
        return True

    @api_process
    async def info(self, request):
        """Return host information."""
        list_addons = []
        for addon in self.sys_addons.list_addons:
            if addon.is_installed:
                list_addons.append({
                    ATTR_NAME: addon.name,
                    ATTR_SLUG: addon.slug,
                    ATTR_DESCRIPTON: addon.description,
                    ATTR_STATE: await addon.state(),
                    ATTR_VERSION: addon.last_version,
                    ATTR_INSTALLED: addon.version_installed,
                    ATTR_REPOSITORY: addon.repository,
                    ATTR_ICON: addon.with_icon,
                    ATTR_LOGO: addon.with_logo,
                })

        return {
            ATTR_VERSION: HASSIO_VERSION,
            ATTR_LAST_VERSION: self.sys_updater.version_hassio,
            ATTR_CHANNEL: self.sys_updater.channel,
            ATTR_ARCH: self.sys_arch,
            ATTR_WAIT_BOOT: self.sys_config.wait_boot,
            ATTR_TIMEZONE: self.sys_config.timezone,
            ATTR_ADDONS: list_addons,
            ATTR_ADDONS_REPOSITORIES: self.sys_config.addons_repositories,
        }

    @api_process
    async def options(self, request):
        """Set supervisor options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_CHANNEL in body:
            self.sys_updater.channel = body[ATTR_CHANNEL]

        if ATTR_TIMEZONE in body:
            self.sys_config.timezone = body[ATTR_TIMEZONE]

        if ATTR_WAIT_BOOT in body:
            self.sys_config.wait_boot = body[ATTR_WAIT_BOOT]

        if ATTR_ADDONS_REPOSITORIES in body:
            new = set(body[ATTR_ADDONS_REPOSITORIES])
            await asyncio.shield(self.sys_addons.load_repositories(new))

        self.sys_updater.save_data()
        self.sys_config.save_data()
        return True

    @api_process
    async def stats(self, request):
        """Return resource information."""
        stats = await self.sys_supervisor.stats()
        if not stats:
            raise RuntimeError("No stats available")

        return {
            ATTR_CPU_PERCENT: stats.cpu_percent,
            ATTR_MEMORY_USAGE: stats.memory_usage,
            ATTR_MEMORY_LIMIT: stats.memory_limit,
            ATTR_NETWORK_RX: stats.network_rx,
            ATTR_NETWORK_TX: stats.network_tx,
            ATTR_BLK_READ: stats.blk_read,
            ATTR_BLK_WRITE: stats.blk_write,
        }

    @api_process
    async def update(self, request):
        """Update supervisor OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_updater.version_hassio)

        if version == self.sys_supervisor.version:
            raise RuntimeError("Version {} is already in use".format(version))

        return await asyncio.shield(
            self.sys_supervisor.update(version))

    @api_process
    async def reload(self, request):
        """Reload addons, config etc."""
        tasks = [
            self.sys_updater.reload(),
        ]
        results, _ = await asyncio.shield(
            asyncio.wait(tasks))

        for result in results:
            if result.exception() is not None:
                raise RuntimeError("Some reload task fails!")

        return True

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return supervisor docker logs."""
        return self.sys_supervisor.logs()
