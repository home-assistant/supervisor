"""Init file for HassIO supervisor rest api."""
import logging

from .util import api_return_ok, api_process_hostcontroll
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

    @api_process_hostcontroll
    async def update(self, request):
        """Update host OS."""
        body = await request.json() or {}
        return await self.host_controll.supervisor_update(
            body.get(ATTR_VERSION))
