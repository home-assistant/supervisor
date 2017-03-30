"""Init file for HassIO homeassistant rest api."""
import logging

from aiohttp.web_exceptions import HTTPServiceUnavailable

from .util import api_return_ok
from ..const import ATTR_VERSION

_LOGGER = logging.getLogger(__name__)


class APIHomeAssistant(object):
    """Handle rest api for homeassistant functions."""

    def __init__(self, config, loop, dock_hass):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.dock_hass = dock_hass

    async def info(self, request):
        """Return host information."""
        return api_return_ok({
            ATTR_VERSION: self.dock_hass.version,
        })

    async def update(self, request):
        """Update host OS."""
        raise HTTPServiceUnavailable()
