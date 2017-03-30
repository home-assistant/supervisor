"""Init file for HassIO supervisor rest api."""
import logging

from aiohttp import web
from aiohttp.web_exceptions import HTTPOk, HTTPMethodNotAllowed

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
        return web.json_response({
            ATTR_VERSION: HASSIO_DOCKER,
        })

    async def update(self, request):
        """Update host OS."""
        body = await request.json() or {}
        if await self.host_controll.supervisor_update(body.get(ATTR_VERSION)):
            raise HTTPOk()
        raise HTTPMethodNotAllowed()
