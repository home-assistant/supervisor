"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_IMAGE, ATTR_CUSTOM, ATTR_BOOT,
    ATTR_PORT, ATTR_PASSWORD, ATTR_SSL, ATTR_WATCHDOG, CONTENT_TYPE_BINARY)
from ..coresys import CoreSysAttributes
from ..validate import NETWORK_PORT

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_BOOT): vol.Boolean(),
    vol.Inclusive(ATTR_IMAGE, 'custom_hass'): vol.Any(None, vol.Coerce(str)),
    vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'):
        vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_PORT): NETWORK_PORT,
    vol.Optional(ATTR_PASSWORD): vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_SSL): vol.Boolean(),
    vol.Optional(ATTR_WATCHDOG): vol.Boolean(),
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHomeAssistant(CoreSysAttributes):
    """Handle rest api for homeassistant functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_VERSION: self._homeassistant.version,
            ATTR_LAST_VERSION: self._homeassistant.last_version,
            ATTR_IMAGE: self._homeassistant.image,
            ATTR_CUSTOM: self._homeassistant.is_custom_image,
            ATTR_BOOT: self._homeassistant.boot,
            ATTR_PORT: self._homeassistant.api_port,
            ATTR_SSL: self._homeassistant.api_ssl,
            ATTR_WATCHDOG: self._homeassistant.watchdog,
        }

    @api_process
    async def options(self, request):
        """Set homeassistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_IMAGE in body:
            self._homeassistant.set_custom(
                body[ATTR_IMAGE], body[ATTR_LAST_VERSION])

        if ATTR_BOOT in body:
            self._homeassistant.boot = body[ATTR_BOOT]

        if ATTR_PORT in body:
            self._homeassistant.api_port = body[ATTR_PORT]

        if ATTR_PASSWORD in body:
            self._homeassistant.api_password = body[ATTR_PASSWORD]

        if ATTR_SSL in body:
            self._homeassistant.api_ssl = body[ATTR_SSL]

        if ATTR_WATCHDOG in body:
            self._homeassistant.watchdog = body[ATTR_WATCHDOG]

        return True

    @api_process
    async def update(self, request):
        """Update homeassistant."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self._homeassistant.last_version)

        if version == self._homeassistant.version:
            raise RuntimeError("Version {} is already in use".format(version))

        return await asyncio.shield(
            self._homeassistant.update(version), loop=self._loop)

    @api_process
    def stop(self, request):
        """Stop homeassistant."""
        return asyncio.shield(self._homeassistant.stop(), loop=self._loop)

    @api_process
    def start(self, request):
        """Start homeassistant."""
        return asyncio.shield(self._homeassistant.run(), loop=self._loop)

    @api_process
    def restart(self, request):
        """Restart homeassistant."""
        return asyncio.shield(self._homeassistant.restart(), loop=self._loop)

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return homeassistant docker logs."""
        return self._homeassistant.logs()

    @api_process
    async def check(self, request):
        """Check config of homeassistant."""
        code, message = await self._homeassistant.check_config()
        if not code:
            raise RuntimeError(message)

        return True
