"""Init file for HassIO supervisor rest api."""
import logging

from aiohttp.web_exceptions import HTTPServiceUnavailable

from .util import api_return_ok, api_return_not_supported
from ..const import ATTR_VERSION, HASSIO_VERSION

_LOGGER = logging.getLogger(__name__)


class APISupervisor(object):
    """Handle rest api for supervisor functions."""

    def __init__(self, config, loop, host_controll):
        """Initialize supervisor rest api part."""
        self.config = config
        self.loop = loop
        self.host_controll = host_controll

    async def info(self, request):
        """Return host information."""
        return api_return_ok({
            ATTR_VERSION: HASSIO_VERSION,
        })

    async def update(self, request):
        """Update host OS."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        body = await request.json() or {}
        if await self.host_controll.supervisor_update(body.get(ATTR_VERSION)):
            return api_return_ok()
        return api_return_not_supported()
