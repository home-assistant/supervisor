"""Init file for HassIO network rest api."""
import logging

import voluptuous as vol

from .util import api_process, api_process_hostcontrol, api_validate
from ..const import ATTR_HOSTNAME

_LOGGER = logging.getLogger(__name__)


SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_HOSTNAME): vol.Coerce(str),
})


class APINetwork(object):
    """Handle rest api for network functions."""

    def __init__(self, config, loop, host_control):
        """Initialize network rest api part."""
        self.config = config
        self.loop = loop
        self.host_control = host_control

    @api_process
    def info(self, request):
        """Show network settings."""
        return {
            ATTR_HOSTNAME: self.host_control.hostname,
        }

    @api_process_hostcontrol
    async def options(self, request):
        """Edit network settings."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        # hostname
        if ATTR_HOSTNAME in body:
            if self.host_control.hostname != body[ATTR_HOSTNAME]:
                await self.host_control.set_hostname(body[ATTR_HOSTNAME])

        return True
