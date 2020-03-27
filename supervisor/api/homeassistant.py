"""Init file for Supervisor Home Assistant RESTful API."""
import asyncio
import logging
from typing import Any, Coroutine, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ARCH,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_BOOT,
    ATTR_CPU_PERCENT,
    ATTR_CUSTOM,
    ATTR_IMAGE,
    ATTR_IP_ADDRESS,
    ATTR_VERSION_LATEST,
    ATTR_MACHINE,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_PERCENT,
    ATTR_MEMORY_USAGE,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_PORT,
    ATTR_REFRESH_TOKEN,
    ATTR_SSL,
    ATTR_VERSION,
    ATTR_WAIT_BOOT,
    ATTR_WATCHDOG,
    CONTENT_TYPE_BINARY,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..validate import docker_image, network_port
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema(
    {
        vol.Optional(ATTR_BOOT): vol.Boolean(),
        vol.Inclusive(ATTR_IMAGE, "custom_hass"): vol.Maybe(docker_image),
        vol.Inclusive(ATTR_VERSION_LATEST, "custom_hass"): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_PORT): network_port,
        vol.Optional(ATTR_SSL): vol.Boolean(),
        vol.Optional(ATTR_WATCHDOG): vol.Boolean(),
        vol.Optional(ATTR_WAIT_BOOT): vol.All(vol.Coerce(int), vol.Range(min=60)),
        vol.Optional(ATTR_REFRESH_TOKEN): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_AUDIO_OUTPUT): vol.Maybe(vol.Coerce(str)),
        vol.Optional(ATTR_AUDIO_INPUT): vol.Maybe(vol.Coerce(str)),
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
            ATTR_VERSION_LATEST: self.sys_homeassistant.latest_version,
            "last_version": self.sys_homeassistant.latest_version,  # Remove end of Q3 2020
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
            ATTR_AUDIO_INPUT: self.sys_homeassistant.audio_input,
            ATTR_AUDIO_OUTPUT: self.sys_homeassistant.audio_output,
        }

    @api_process
    async def options(self, request: web.Request) -> None:
        """Set Home Assistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_IMAGE in body and ATTR_VERSION_LATEST in body:
            self.sys_homeassistant.image = body[ATTR_IMAGE]
            self.sys_homeassistant.latest_version = body[ATTR_VERSION_LATEST]

        if ATTR_BOOT in body:
            self.sys_homeassistant.boot = body[ATTR_BOOT]

        if ATTR_PORT in body:
            self.sys_homeassistant.api_port = body[ATTR_PORT]

        if ATTR_SSL in body:
            self.sys_homeassistant.api_ssl = body[ATTR_SSL]

        if ATTR_WATCHDOG in body:
            self.sys_homeassistant.watchdog = body[ATTR_WATCHDOG]

        if ATTR_WAIT_BOOT in body:
            self.sys_homeassistant.wait_boot = body[ATTR_WAIT_BOOT]

        if ATTR_REFRESH_TOKEN in body:
            self.sys_homeassistant.refresh_token = body[ATTR_REFRESH_TOKEN]

        if ATTR_AUDIO_INPUT in body:
            self.sys_homeassistant.audio_input = body[ATTR_AUDIO_INPUT]

        if ATTR_AUDIO_OUTPUT in body:
            self.sys_homeassistant.audio_output = body[ATTR_AUDIO_OUTPUT]

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
