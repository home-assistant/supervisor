"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process_hostcontrol, api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_TYPE, ATTR_HOSTNAME, ATTR_FEATURES,
    ATTR_OS)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})

class APIHost(CoreSysAttributes):
    """Handle rest api for host functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_TYPE: self._host_control.type,
            ATTR_VERSION: self._host_control.version,
            ATTR_LAST_VERSION: self._host_control.last_version,
            ATTR_FEATURES: self._host_control.features,
            ATTR_HOSTNAME: self._host_control.hostname,
            ATTR_OS: self._host_control.os_info,
        }

    @api_process_hostcontrol
    def reboot(self, request):
        """Reboot host."""
        return self._host_control.reboot()

    @api_process_hostcontrol
    def shutdown(self, request):
        """Poweroff host."""
        return self._host_control.shutdown()

    @api_process_hostcontrol
    async def reload(self, request):
        """Reload host data."""
        await self._host_control.load()
        return True

    @api_process_hostcontrol
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self._host_control.last_version)

        if version == self._host_control.version:
            raise RuntimeError(f"Version {version} is already in use")

        return await asyncio.shield(
            self._host_control.update(version=version), loop=self._loop)
