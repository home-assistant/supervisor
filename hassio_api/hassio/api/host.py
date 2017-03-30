"""Init file for HassIO host rest api."""
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPServiceUnavailable

from .util import api_return_ok, api_return_not_supported
from ..const import ATTR_VERSION

_LOGGER = logging.getLogger(__name__)


class APIHost(object):
    """Handle rest api for host functions."""

    def __init__(self, config, loop, host_controll):
        """Initialize host rest api part."""
        self.config = config
        self.loop = loop
        self.host_controll = host_controll

    async def info(self, request):
        """Return host information."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        host_info = await self.host_controll.info()
        if host_info:
            return web.json_response(host_info)
        return api_return_not_supported()

    async def reboot(self, request):
        """Reboot host."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        if await self.host_controll.reboot():
            return api_return_ok()
        return api_return_not_supported()

    async def shutdown(self, request):
        """Poweroff host."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        if await self.host_controll.shutdown():
            return api_return_ok()
        return api_return_not_supported()

    async def network_info(self, request):
        """Edit network settings."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        return api_return_not_supported()

    async def network_update(self, request):
        """Edit network settings."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        return api_return_not_supported()

    async def update(self, request):
        """Update host OS."""
        if not self.host_controll.active:
            raise HTTPServiceUnavailable()

        body = await request.json() or {}
        if await self.host_controll.host_update(body.get(ATTR_VERSION)):
            return api_return_ok()
        return api_return_not_supported()
