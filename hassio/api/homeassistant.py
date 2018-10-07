"""Init file for Hass.io Home Assistant RESTful API."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_IMAGE, ATTR_CUSTOM, ATTR_BOOT,
    ATTR_PORT, ATTR_PASSWORD, ATTR_SSL, ATTR_WATCHDOG, ATTR_CPU_PERCENT,
    ATTR_MEMORY_USAGE, ATTR_MEMORY_LIMIT, ATTR_NETWORK_RX, ATTR_NETWORK_TX,
    ATTR_BLK_READ, ATTR_BLK_WRITE, ATTR_WAIT_BOOT, ATTR_MACHINE,
    ATTR_REFRESH_TOKEN, CONTENT_TYPE_BINARY)
from ..coresys import CoreSysAttributes
from ..validate import NETWORK_PORT, DOCKER_IMAGE
from ..exceptions import APIError

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_BOOT): vol.Boolean(),
    vol.Inclusive(ATTR_IMAGE, 'custom_hass'):
        vol.Maybe(vol.Coerce(str)),
    vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'):
        vol.Any(None, DOCKER_IMAGE),
    vol.Optional(ATTR_PORT): NETWORK_PORT,
    vol.Optional(ATTR_PASSWORD): vol.Maybe(vol.Coerce(str)),
    vol.Optional(ATTR_SSL): vol.Boolean(),
    vol.Optional(ATTR_WATCHDOG): vol.Boolean(),
    vol.Optional(ATTR_WAIT_BOOT):
        vol.All(vol.Coerce(int), vol.Range(min=60)),
    vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHomeAssistant(CoreSysAttributes):
    """Handle RESTful API for Home Assistant functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_VERSION: self.sys_homeassistant.version,
            ATTR_LAST_VERSION: self.sys_homeassistant.last_version,
            ATTR_MACHINE: self.sys_homeassistant.machine,
            ATTR_IMAGE: self.sys_homeassistant.image,
            ATTR_CUSTOM: self.sys_homeassistant.is_custom_image,
            ATTR_BOOT: self.sys_homeassistant.boot,
            ATTR_PORT: self.sys_homeassistant.api_port,
            ATTR_SSL: self.sys_homeassistant.api_ssl,
            ATTR_WATCHDOG: self.sys_homeassistant.watchdog,
            ATTR_WAIT_BOOT: self.sys_homeassistant.wait_boot,
        }

    @api_process
    async def options(self, request):
        """Set Home Assistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_IMAGE in body and ATTR_LAST_VERSION in body:
            self.sys_homeassistant.image = body[ATTR_IMAGE]
            self.sys_homeassistant.last_version = body[ATTR_LAST_VERSION]

        if ATTR_BOOT in body:
            self.sys_homeassistant.boot = body[ATTR_BOOT]

        if ATTR_PORT in body:
            self.sys_homeassistant.api_port = body[ATTR_PORT]

        if ATTR_PASSWORD in body:
            self.sys_homeassistant.api_password = body[ATTR_PASSWORD]

        if ATTR_SSL in body:
            self.sys_homeassistant.api_ssl = body[ATTR_SSL]

        if ATTR_WATCHDOG in body:
            self.sys_homeassistant.watchdog = body[ATTR_WATCHDOG]

        if ATTR_WAIT_BOOT in body:
            self.sys_homeassistant.wait_boot = body[ATTR_WAIT_BOOT]

        if ATTR_REFRESH_TOKEN in body:
            self.sys_homeassistant.refresh_token = body[ATTR_REFRESH_TOKEN]

        self.sys_homeassistant.save_data()

    @api_process
    async def stats(self, request):
        """Return resource information."""
        stats = await self.sys_homeassistant.stats()
        if not stats:
            raise APIError("No stats available")

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
        """Update Home Assistant."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_homeassistant.last_version)

        await asyncio.shield(self.sys_homeassistant.update(version))

    @api_process
    def stop(self, request):
        """Stop Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.stop())

    @api_process
    def start(self, request):
        """Start Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.start())

    @api_process
    def restart(self, request):
        """Restart Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.restart())

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return Home Assistant Docker logs."""
        return self.sys_homeassistant.logs()

    @api_process
    async def check(self, request):
        """Check configuration of Home Assistant."""
        result = await self.sys_homeassistant.check_config()
        if not result.valid:
            raise APIError(result.log)
