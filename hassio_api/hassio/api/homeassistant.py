"""Init file for HassIO homeassistant rest api."""
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPMethodNotAllowed

from ..const import ATTR_VERSION

_LOGGER = logging.getLogger(__name__)


class APIHomeAssistant(object):
    """Handle rest api for homeassistant functions."""

    def __init__(self, config, loop, dock_hass):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.dock_hass = hass

    async def info(self, request):
        """Return host information."""
        return web.json_response({
            ATTR_VERSION: self.dock_hass.version,
        })

    async def update(self, request):
        """Update host OS."""
        raise HTTPMethodNotAllowed()
