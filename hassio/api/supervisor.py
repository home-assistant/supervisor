"""Init file for HassIO supervisor rest api."""
import logging

from .util import api_process, api_process_hostcontroll, json_loads
from ..const import ATTR_VERSION, ATTR_CURRENT, ATTR_BETA, HASSIO_VERSION

_LOGGER = logging.getLogger(__name__)


class APISupervisor(object):
    """Handle rest api for supervisor functions."""

    def __init__(self, config, loop, host_controll):
        """Initialize supervisor rest api part."""
        self.config = config
        self.loop = loop
        self.host_controll = host_controll

    @api_process
    async def info(self, request):
        """Return host information."""
        info = {
            ATTR_VERSION: HASSIO_VERSION,
            ATTR_CURRENT: self.config.current_hassio,
            ATTR_BETA: self.config.upstream_beta,
        }

        return info

    @api_process
    async def options(self, request):
        """Set supervisor options."""
        body = await request.json(loads=json_loads)

        if ATTR_BETA in body:
            self.config.upstream_beta = body[ATTR_BETA]

        return self.config.save()

    @api_process_hostcontroll
    async def update(self, request):
        """Update host OS."""
        body = await request.json(loads=json_loads)
        version = body.get(ATTR_VERSION, self.config.current_hassio)

        if version == HASSIO_VERSION:
            raise RuntimeError("%s is already in use.", version)

        return await self.host_controll.supervisor_update(version=version)
