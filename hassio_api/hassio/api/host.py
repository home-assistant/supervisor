"""Init file for HassIO rest api."""
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPOk, HTTPMethodNotAllowed

_LOGGER = logging.getLogger(__name__)


class APIHost(object):
    """Handle rest api for host functions."""

    def __init__(self, config, loop, host_controll):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.host_controll

    async def info(self, request):
        """Return host information."""
        host_info = await self.host_controll.info()
        if host_info:
            return web.json_response(host_info)
        raise HTTPMethodNotAllowed()

    async def reboot(self, request):
        """Reboot host."""
        if await self.host_controll.reboot():
            raise HTTPOk()
        raise HTTPMethodNotAllowed()

    async def shutdown(self, request):
        """Poweroff host."""
        if await self.host_controll.shutdown():
            raise HTTPOk()
        raise HTTPMethodNotAllowed()

    async def network_info(self, request):
        """Edit network settings."""
        raise HTTPMethodNotAllowed()

    async def network_update(self, request):
        """Edit network settings."""
        raise HTTPMethodNotAllowed()

    async def update_host(self, request):
        """Update host OS."""
        if await self.host_controll.host_update():
            raise HTTPOk()
        raise HTTPMethodNotAllowed()
