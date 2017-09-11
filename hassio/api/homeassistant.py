"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_DEVICES, ATTR_IMAGE, ATTR_CUSTOM,
    ATTR_BOOT, CONTENT_TYPE_BINARY)
from ..validate import HASS_DEVICES

_LOGGER = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_DEVICES): HASS_DEVICES,
    vol.Optional(ATTR_BOOT): vol.Boolean(),
    vol.Inclusive(ATTR_IMAGE, 'custom_hass'): vol.Any(None, vol.Coerce(str)),
    vol.Inclusive(ATTR_LAST_VERSION, 'custom_hass'):
        vol.Any(None, vol.Coerce(str)),
})

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHomeAssistant(object):
    """Handle rest api for homeassistant functions."""

    def __init__(self, config, loop, homeassistant):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.homeassistant = homeassistant

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_VERSION: self.homeassistant.version,
            ATTR_LAST_VERSION: self.homeassistant.last_version,
            ATTR_IMAGE: self.homeassistant.image,
            ATTR_DEVICES: self.homeassistant.devices,
            ATTR_CUSTOM: self.homeassistant.is_custom_image,
            ATTR_BOOT: self.homeassistant.boot,
        }

    @api_process
    async def options(self, request):
        """Set homeassistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_DEVICES in body:
            self.homeassistant.devices = body[ATTR_DEVICES]

        if ATTR_IMAGE in body:
            self.homeassistant.set_custom(
                body[ATTR_IMAGE], body[ATTR_LAST_VERSION])

        if ATTR_BOOT in body:
            self.homeassistant.boot = body[ATTR_BOOT]

        return True

    @api_process
    async def update(self, request):
        """Update homeassistant."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.homeassistant.last_version)

        if version == self.homeassistant.version:
            raise RuntimeError("Version {} is already in use".format(version))

        return await asyncio.shield(
            self.homeassistant.update(version), loop=self.loop)

    @api_process
    def stop(self, request):
        """Stop homeassistant."""
        return asyncio.shield(self.homeassistant.stop(), loop=self.loop)

    @api_process
    def start(self, request):
        """Start homeassistant."""
        return asyncio.shield(self.homeassistant.run(), loop=self.loop)

    @api_process
    def restart(self, request):
        """Restart homeassistant."""
        return asyncio.shield(self.homeassistant.restart(), loop=self.loop)

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return homeassistant docker logs."""
        return self.homeassistant.logs()

    @api_process
    async def check(self, request):
        """Check config of homeassistant."""
        code, message = await self.homeassistant.check_config()
        if not code:
            raise RuntimeError(message)

        return True
