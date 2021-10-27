"""Init file for Supervisor host RESTful API."""
import asyncio
from typing import Awaitable

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_CHASSIS,
    ATTR_CPE,
    ATTR_DEPLOYMENT,
    ATTR_DESCRIPTON,
    ATTR_DISK_FREE,
    ATTR_DISK_LIFE_TIME,
    ATTR_DISK_TOTAL,
    ATTR_DISK_USED,
    ATTR_FEATURES,
    ATTR_HOSTNAME,
    ATTR_KERNEL,
    ATTR_NAME,
    ATTR_OPERATING_SYSTEM,
    ATTR_SERVICES,
    ATTR_STATE,
    ATTR_TIMEZONE,
    CONTENT_TYPE_BINARY,
)
from ..coresys import CoreSysAttributes
from .const import (
    ATTR_AGENT_VERSION,
    ATTR_APPARMOR,
    ATTR_BOOT_TIMESTAMP,
    ATTR_DT_SYNCHRONIZED,
    ATTR_DT_UTC,
    ATTR_STARTUP_TIME,
    ATTR_USE_NTP,
    ATTR_USE_RTC,
)
from .utils import api_process, api_process_raw, api_validate

SERVICE = "service"

SCHEMA_OPTIONS = vol.Schema({vol.Optional(ATTR_HOSTNAME): str})


class APIHost(CoreSysAttributes):
    """Handle RESTful API for host functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_AGENT_VERSION: self.sys_dbus.agent.version,
            ATTR_CHASSIS: self.sys_host.info.chassis,
            ATTR_CPE: self.sys_host.info.cpe,
            ATTR_DEPLOYMENT: self.sys_host.info.deployment,
            ATTR_DISK_FREE: self.sys_host.info.free_space,
            ATTR_DISK_TOTAL: self.sys_host.info.total_space,
            ATTR_DISK_USED: self.sys_host.info.used_space,
            ATTR_DISK_LIFE_TIME: self.sys_host.info.disk_life_time,
            ATTR_FEATURES: self.sys_host.features,
            ATTR_HOSTNAME: self.sys_host.info.hostname,
            ATTR_KERNEL: self.sys_host.info.kernel,
            ATTR_OPERATING_SYSTEM: self.sys_host.info.operating_system,
            ATTR_APPARMOR: self.sys_host.apparmor.version,
            ATTR_TIMEZONE: self.sys_host.info.timezone,
            ATTR_DT_UTC: self.sys_host.info.dt_utc,
            ATTR_DT_SYNCHRONIZED: self.sys_host.info.dt_synchronized,
            ATTR_USE_NTP: self.sys_host.info.use_ntp,
            ATTR_USE_RTC: self.sys_host.info.use_rtc,
            ATTR_STARTUP_TIME: self.sys_host.info.startup_time,
            ATTR_BOOT_TIMESTAMP: self.sys_host.info.boot_timestamp,
        }

    @api_process
    async def options(self, request):
        """Edit host settings."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        # hostname
        if ATTR_HOSTNAME in body:
            await asyncio.shield(
                self.sys_host.control.set_hostname(body[ATTR_HOSTNAME])
            )

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
        return asyncio.shield(
            asyncio.wait(
                [self.sys_host.reload(), self.sys_resolution.evaluate.evaluate_system()]
            )
        )

    @api_process
    async def services(self, request):
        """Return list of available services."""
        services = []
        for unit in self.sys_host.services:
            services.append(
                {
                    ATTR_NAME: unit.name,
                    ATTR_DESCRIPTON: unit.description,
                    ATTR_STATE: unit.state,
                }
            )

        return {ATTR_SERVICES: services}

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

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return host kernel logs."""
        return self.sys_host.info.get_dmesg()
