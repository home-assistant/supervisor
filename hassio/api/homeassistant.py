"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import ATTR_VERSION, ATTR_LAST_VERSION, ATTR_DEVICES

_LOGGER = logging.getLogger(__name__)


SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_DEVICES): [vol.Coerce(str)],
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
            ATTR_LAST_VERSION: self.config.last_homeassistant,
            ATTR_DEVICES: self.config.homeassistant_devices,
        }

    @api_process
    async def options(self, request):
        """Set homeassistant options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_DEVICES in body:
            self.config.homeassistant_devices = body[ATTR_DEVICES]

        return True

    @api_process
    async def update(self, request):
        """Update homeassistant."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.config.last_homeassistant)

        if self.homeassistant.in_progress:
            raise RuntimeError("Other task is in progress")

        if version == self.homeassistant.version:
            raise RuntimeError("Version is already in use")

        return await asyncio.shield(
            self.homeassistant.update(version), loop=self.loop)

    @api_process
    async def restart(self, request):
        """Restart homeassistant."""
        if self.homeassistant.in_progress:
            raise RuntimeError("Other task is in progress")

        return await asyncio.shield(
            self.homeassistant.restart(), loop=self.loop)

    @api_process_raw
    def logs(self, request):
        """Return homeassistant docker logs.

        Return a coroutine.
        """
        return self.homeassistant.logs()
