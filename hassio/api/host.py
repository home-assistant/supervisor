"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
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
            ATTR_TYPE: ,
            ATTR_VERSION: ,
            ATTR_LAST_VERSION: ,
            ATTR_FEATURES: self.sys_host.features,
            ATTR_HOSTNAME: ,
            ATTR_OS: ,
        }

    @api_process
    def reboot(self, request):
        """Reboot host."""
        return self.sys_host.power.reboot()

    @api_process
    def shutdown(self, request):
        """Poweroff host."""
        return self.sys_host.power.shutdown()

    @api_process
    def reload(self, request):
        """Reload host data."""
        return self._host_control.load()

    @api_process
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self._host_control.last_version)

        if version == self._host_control.version:
            raise RuntimeError(f"Version {version} is already in use")

        return await asyncio.shield(
            self._host_control.update(version=version))
