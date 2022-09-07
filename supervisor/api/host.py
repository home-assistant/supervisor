"""Init file for Supervisor host RESTful API."""
import asyncio
import logging
from typing import Awaitable

from aiohttp import web
from aiohttp.hdrs import ACCEPT, RANGE
import voluptuous as vol

from supervisor.exceptions import APIError

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
)
from ..coresys import CoreSysAttributes
from .const import (
    ATTR_AGENT_VERSION,
    ATTR_APPARMOR_VERSION,
    ATTR_BOOT_TIMESTAMP,
    ATTR_BROADCAST_LLMNR,
    ATTR_BROADCAST_MDNS,
    ATTR_DT_SYNCHRONIZED,
    ATTR_DT_UTC,
    ATTR_LLMNR_HOSTNAME,
    ATTR_STARTUP_TIME,
    ATTR_USE_NTP,
    CONTENT_TYPE_BINARY,
    CONTENT_TYPE_TEXT,
)
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SERVICE = "service"
IDENTIFIER = "identifier"
BOOTID = "bootid"

SCHEMA_OPTIONS = vol.Schema({vol.Optional(ATTR_HOSTNAME): str})


class APIHost(CoreSysAttributes):
    """Handle RESTful API for host functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_AGENT_VERSION: self.sys_dbus.agent.version,
            ATTR_APPARMOR_VERSION: self.sys_host.apparmor.version,
            ATTR_CHASSIS: self.sys_host.info.chassis,
            ATTR_CPE: self.sys_host.info.cpe,
            ATTR_DEPLOYMENT: self.sys_host.info.deployment,
            ATTR_DISK_FREE: self.sys_host.info.free_space,
            ATTR_DISK_TOTAL: self.sys_host.info.total_space,
            ATTR_DISK_USED: self.sys_host.info.used_space,
            ATTR_DISK_LIFE_TIME: self.sys_host.info.disk_life_time,
            ATTR_FEATURES: self.sys_host.features,
            ATTR_HOSTNAME: self.sys_host.info.hostname,
            ATTR_LLMNR_HOSTNAME: self.sys_host.info.llmnr_hostname,
            ATTR_KERNEL: self.sys_host.info.kernel,
            ATTR_OPERATING_SYSTEM: self.sys_host.info.operating_system,
            ATTR_TIMEZONE: self.sys_host.info.timezone,
            ATTR_DT_UTC: self.sys_host.info.dt_utc,
            ATTR_DT_SYNCHRONIZED: self.sys_host.info.dt_synchronized,
            ATTR_USE_NTP: self.sys_host.info.use_ntp,
            ATTR_STARTUP_TIME: self.sys_host.info.startup_time,
            ATTR_BOOT_TIMESTAMP: self.sys_host.info.boot_timestamp,
            ATTR_BROADCAST_LLMNR: self.sys_host.info.broadcast_llmnr,
            ATTR_BROADCAST_MDNS: self.sys_host.info.broadcast_mdns,
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
        return asyncio.shield(self.sys_host.reload())

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
        return [asyncio.shield(self.sys_host.services.start(unit))]

    @api_process
    def service_stop(self, request):
        """Stop a service."""
        unit = request.match_info.get(SERVICE)
        return [asyncio.shield(self.sys_host.services.stop(unit))]

    @api_process
    def service_reload(self, request):
        """Reload a service."""
        unit = request.match_info.get(SERVICE)
        return [asyncio.shield(self.sys_host.services.reload(unit))]

    @api_process
    def service_restart(self, request):
        """Restart a service."""
        unit = request.match_info.get(SERVICE)
        return [asyncio.shield(self.sys_host.services.restart(unit))]

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return host kernel logs."""
        return self.sys_host.info.get_dmesg()

    @api_process
    async def advanced_logs(
        self, request: web.Request, follow=False
    ) -> web.StreamResponse:
        """Return systemd-journald logs."""
        params = {}
        if IDENTIFIER in request.match_info:
            params["SYSLOG_IDENTIFIER"] = request.match_info.get(IDENTIFIER)
        if BOOTID in request.match_info:
            params["_BOOT_ID"] = request.match_info.get(BOOTID)
        if follow:
            params["follow"] = ""

        if ACCEPT in request.headers and request.headers[ACCEPT] not in [
            CONTENT_TYPE_TEXT,
            "*/*",
        ]:
            raise APIError(
                "Invalid content type requested. Only text/plain supported for now."
            )

        range_header = request.headers.get(RANGE)

        async with self.sys_host.logs.journald_logs(params, range_header) as resp:
            try:
                response = web.StreamResponse()
                response.content_type = CONTENT_TYPE_TEXT
                await response.prepare(request)
                async for data in resp.content:
                    await response.write(data)
            except ConnectionResetError as ex:
                raise APIError(
                    "Connection reset when trying to fetch data from systemd-journald."
                ) from ex
            return response
