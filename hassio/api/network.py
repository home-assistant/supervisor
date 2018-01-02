"""Init file for HassIO network rest api."""
import logging

import voluptuous as vol

from .utils import api_process, api_process_hostcontrol, api_validate
from ..const import ATTR_HOSTNAME
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_HOSTNAME): vol.Coerce(str),
})


class APINetwork(CoreSysAttributes):
    """Handle rest api for network functions."""

    @api_process
    async def info(self, request):
        """Show network settings."""
        return {
            ATTR_HOSTNAME: self._host_control.hostname,
        }

    @api_process_hostcontrol
    async def options(self, request):
        """Edit network settings."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        # hostname
        if ATTR_HOSTNAME in body:
            if self._host_control.hostname != body[ATTR_HOSTNAME]:
                await self._host_control.set_hostname(body[ATTR_HOSTNAME])

        return True
