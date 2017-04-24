"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_process_raw, api_validate
from ..const import ATTR_VERSION, ATTR_CURRENT

_LOGGER = logging.getLogger(__name__)

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
        info = {
            ATTR_VERSION: self.homeassistant.version,
            ATTR_CURRENT: self.config.current_homeassistant,
        }

        return info

    @api_process
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.config.current_homeassistant)

        if self.homeassistant.in_progress:
            raise RuntimeError("Other task is in progress")

        if version == self.homeassistant.version:
            raise RuntimeError("Version is already in use")

        return await asyncio.shield(
            self.homeassistant.update(version), loop=self.loop)

    @api_process_raw
    def logs(self, request):
        """Return homeassistant docker logs.

        Return a coroutine.
        """
        return self.homeassistant.logs()
