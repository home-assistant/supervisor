"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_DEVICES, ATTR_IMAGE, ATTR_CUSTOM,
    CONTENT_TYPE_BINARY)
from ..validate import HASS_DEVICES

_LOGGER = logging.getLogger(__name__)


SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_DEVICES): HASS_DEVICES,
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
    def restart(self, request):
        """Restart homeassistant.

        Return a coroutine.
        """
        return asyncio.shield(self.homeassistant.restart(), loop=self.loop)

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request):
        """Return homeassistant docker logs.

        Return a coroutine.
        """
        return self.homeassistant.logs()
