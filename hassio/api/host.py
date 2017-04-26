"""Init file for HassIO host rest api."""
import logging

import voluptuous as vol

from .util import api_process_hostcontrol, api_process, api_validate
from ..const import ATTR_VERSION

_LOGGER = logging.getLogger(__name__)

UNKNOWN = 'unknown'

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHost(object):
    """Handle rest api for host functions."""

    def __init__(self, config, loop, host_control):
        """Initialize host rest api part."""
        self.config = config
        self.loop = loop
        self.host_control = host_control

    @api_process
    async def info(self, request):
        """Return host information."""
        if not self.host_control.active:
            info = {
                'os': UNKNOWN,
                'version': UNKNOWN,
                'current': UNKNOWN,
                'level': 0,
                'hostname': UNKNOWN,
            }
            return info

        return await self.host_control.info()

    @api_process_hostcontrol
    def reboot(self, request):
        """Reboot host."""
        return self.host_control.reboot()

    @api_process_hostcontrol
    def shutdown(self, request):
        """Poweroff host."""
        return self.host_control.shutdown()

    @api_process_hostcontrol
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION)

        if version == self.host_control.version:
            raise RuntimeError("Version is already in use")

        return await self.host_control.host_update(version=version)
