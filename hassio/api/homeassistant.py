"""Init file for Hass.io Home Assistant RESTful API."""
import asyncio
import logging
from typing import Coroutine, Dict, Any

import voluptuous as vol
from aiohttp import web

from ..const import (
    ATTR_ARCH,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_BOOT,
    ATTR_CPU_PERCENT,
    ATTR_CUSTOM,
    ATTR_IMAGE,
    ATTR_LAST_VERSION,
    ATTR_MACHINE,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_USAGE,
    ATTR_MEMORY_PERCENT,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    ATTR_IP_ADDRESS,
    CONTENT_TYPE_BINARY,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..validate import DOCKER_IMAGE, NETWORK_PORT
from .utils import api_process, api_process_raw, api_validate

_LOGGER = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_BOOT): vol.Boolean(),
        vol.Inclusive(ATTR_IMAGE, "custom_hass"): vol.Maybe(DOCKER_IMAGE),
        vol.Inclusive(ATTR_LAST_VERSION, "custom_hass"): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_PORT): NETWORK_PORT,
        vol.Optional(ATTR_PASSWORD): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_SSL): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG): vol.Boolean(),
        vol.Optional(ATTR_WAIT_BOOT): vol.All(vol.Coerce(int), vol.Range(min=60)),
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
    }
)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): vol.Coerce(str)})


class APIHomeAssistant(CoreSysAttributes):
    """Handle RESTful API for Home Assistant functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return host information."""
        return {
            ATTR_VERSION: self.sys_homeassistant.version,
            ATTR_LAST_VERSION: self.sys_homeassistant.latest_version,
            ATTR_MACHINE: self.sys_homeassistant.machine,
            ATTR_IP_ADDRESS: str(self.sys_homeassistant.ip_address),
            ATTR_ARCH: self.sys_homeassistant.arch,
            ATTR_IMAGE: self.sys_homeassistant.image,
            ATTR_CUSTOM: self.sys_homeassistant.is_custom_image,
            ATTR_BOOT: self.sys_homeassistant.boot,
            ATTR_PORT: self.sys_homeassistant.api_port,
            ATTR_SSL: self.sys_homeassistant.api_ssl,
            ATTR_WATCHDOG: self.sys_homeassistant.watchdog,
            ATTR_WAIT_BOOT: self.sys_homeassistant.wait_boot,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set Home Assistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_IMAGE in body and ATTR_LAST_VERSION in body:
            self.sys_homeassistant.image = body[ATTR_IMAGE]
            self.sys_homeassistant.latest_version = body[ATTR_LAST_VERSION]

        if ATTR_BOOT in body:
            self.sys_homeassistant.boot = body[ATTR_BOOT]

        if ATTR_PORT in body:
            self.sys_homeassistant.api_port = body[ATTR_PORT]

        if ATTR_PASSWORD in body:
            self.sys_homeassistant.api_password = body[ATTR_PASSWORD]
            self.sys_homeassistant.refresh_token = None

        if ATTR_SSL in body:
            self.sys_homeassistant.api_ssl = body[ATTR_SSL]

        if ATTR_WATCHDOG in body:
            self.sys_homeassistant.watchdog = body[ATTR_WATCHDOG]

        if ATTR_WAIT_BOOT in body:
            self.sys_homeassistant.wait_boot = body[ATTR_WAIT_BOOT]

        if ATTR_REFRESH_TOKEN in body:
            self.sys_homeassistant.refresh_token = body[ATTR_REFRESH_TOKEN]
            self.sys_homeassistant.api_password = None

        self.sys_homeassistant.save_data()

    @api_process
    async def stats(self, request: web.Request) -> Dict[Any, str]:
        """Return resource information."""
        stats = await self.sys_homeassistant.stats()
        if not stats:
            raise APIError("No stats available")

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
        """Update Home Assistant."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_homeassistant.latest_version)

        await asyncio.shield(self.sys_homeassistant.update(version))

    @api_process
    def stop(self, request: web.Request) -> Coroutine:
        """Stop Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.stop())

    @api_process
    def start(self, request: web.Request) -> Coroutine:
        """Start Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.start())

    @api_process
    def restart(self, request: web.Request) -> Coroutine:
        """Restart Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.restart())

    @api_process
    def rebuild(self, request: web.Request) -> Coroutine:
        """Rebuild Home Assistant."""
        return asyncio.shield(self.sys_homeassistant.rebuild())

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Coroutine:
        """Return Home Assistant Docker logs."""
        return self.sys_homeassistant.logs()

    @api_process
    async def check(self, request: web.Request) -> None:
        """Check configuration of Home Assistant."""
        result = await self.sys_homeassistant.check_config()
        if not result.valid:
            raise APIError(result.log)
