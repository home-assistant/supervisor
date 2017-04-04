"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

from .util import api_process, json_loads
from ..const import ATTR_VERSION

_LOGGER = logging.getLogger(__name__)


class APIHomeAssistant(object):
    """Handle rest api for homeassistant functions."""

    def __init__(self, config, loop, dock_hass):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.dock_hass = dock_hass

    @api_process
    async def info(self, request):
        """Return host information."""
        info = {
            ATTR_VERSION: self.dock_hass.version,
        }

        return info

    @api_process
    async def update(self, request):
        """Update host OS."""
        body = await request.json(loads=json_loads)
        version = body.get(ATTR_VERSION, self.config.current_homeassistant)

        if self.dock_hass.in_progress:
            raise RuntimeError("Other task is in progress!")

        return await asyncio.shield(self.dock_hass.update(version))
