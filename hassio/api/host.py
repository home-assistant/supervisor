"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_HOSTNAME, ATTR_FEATURES, ATTR_KERNEL, ATTR_OPERATING_SYSTEM,
    ATTR_CHASSIS, ATTR_DEPLOYMENT, ATTR_STATE, ATTR_NAME, ATTR_DESCRIPTON,
    ATTR_SERVICES, ATTR_CPE)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SERVICE = 'service'

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
            ATTR_CPE: self.sys_host.info.cpe,
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
    async def services(self, request):
        """Return list of available services."""
        services = []
        for unit in self.sys_host.services:
            services.append({
                ATTR_NAME: unit.name,
                ATTR_DESCRIPTON: unit.description,
                ATTR_STATE: unit.state,
            })

        return {
            ATTR_SERVICES: services
        }

    @api_process
    def service_start(self, request):
        """Start a service."""
        unit = request.match_info.get(SERVICE)
        return asyncio.shield(self.sys_host.services.start(unit))

    @api_process
    def service_stop(self, request):
        """Stop a service."""
        unit = request.match_info.get(SERVICE)
        return asyncio.shield(self.sys_host.services.stop(unit))

    @api_process
    def service_reload(self, request):
        """Reload a service."""
        unit = request.match_info.get(SERVICE)
        return asyncio.shield(self.sys_host.services.reload(unit))

    @api_process
    def service_restart(self, request):
        """Restart a service."""
        unit = request.match_info.get(SERVICE)
        return asyncio.shield(self.sys_host.services.restart(unit))
