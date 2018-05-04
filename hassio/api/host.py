"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_HOSTNAME, ATTR_FEATURES, ATTR_KERNEL,
    ATTR_TYPE, ATTR_OPERATING_SYSTEM, ATTR_CHASSIS, ATTR_DEPLOYMENT)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})

SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_HOSTNAME): vol.Coerce(str),
})


class APIHost(CoreSysAttributes):
    """Handle rest api for host functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_CHASSIS: self.sys_host.info.chassis,
            ATTR_VERSION: None,
            ATTR_LAST_VERSION: None,
            ATTR_TYPE: None,
            ATTR_FEATURES: self.sys_host.supperted_features,
            ATTR_HOSTNAME: self.sys_host.info.hostname,
            ATTR_OPERATING_SYSTEM: self.sys_host.info.operating_system,
            ATTR_DEPLOYMENT: self.sys_host.info.deployment,
            ATTR_KERNEL: self.sys_host.info.kernel,
        }

    @api_process
    async def options(self, request):
        """Edit host settings."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        # hostname
        if ATTR_HOSTNAME in body:
            await asyncio.shield(
                self.sys_host.control.set_hostname(body[ATTR_HOSTNAME]))

    @api_process
    def reboot(self, request):
        """Reboot host."""
        return asyncio.shield(self.sys_host.control.reboot())

    @api_process
    def shutdown(self, request):
        """Poweroff host."""
        return asyncio.shield(self.sys_host.control.shutdown())

    @api_process
    def reload(self, request):
        """Reload host data."""
        return asyncio.shield(self.sys_host.reload())

    @api_process
    async def update(self, request):
        """Update host OS."""
        pass
        # body = await api_validate(SCHEMA_VERSION, request)
        # version = body.get(ATTR_VERSION, self.sys_host.last_version)
