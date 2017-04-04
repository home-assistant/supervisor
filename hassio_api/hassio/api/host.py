"""Init file for HassIO host rest api."""
import logging

from .util import api_process_hostcontroll, json_loads
from ..const import ATTR_VERSION

_LOGGER = logging.getLogger(__name__)


class APIHost(object):
    """Handle rest api for host functions."""

    def __init__(self, config, loop, host_controll):
        """Initialize host rest api part."""
        self.config = config
        self.loop = loop
        self.host_controll = host_controll

    @api_process_hostcontroll
    def info(self, request):
        """Return host information."""
        return self.host_controll.info()

    @api_process_hostcontroll
    def reboot(self, request):
        """Reboot host."""
        return self.host_controll.reboot()

    @api_process_hostcontroll
    def shutdown(self, request):
        """Poweroff host."""
        return self.host_controll.shutdown()

    @api_process_hostcontroll
    def network_info(self, request):
        """Edit network settings."""
        pass

    @api_process_hostcontroll
    def network_update(self, request):
        """Edit network settings."""
        pass

    @api_process_hostcontroll
    async def update(self, request):
        """Update host OS."""
        body = await request.json(loads=json_loads)
        version = body.get(ATTR_VERSION)

        if version == self.host_controll.version:
            raise RuntimeError("%s is already in use.", version)

        return await self.host_controll.host_update(version=version)
