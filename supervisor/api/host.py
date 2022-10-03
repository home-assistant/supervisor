"""Init file for Supervisor host RESTful API."""
import asyncio
from contextlib import suppress
import logging

from aiohttp import web
from aiohttp.hdrs import ACCEPT, RANGE
import voluptuous as vol
from voluptuous.error import CoerceInvalid

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
from ..exceptions import APIError, HostLogError
from ..host.const import PARAM_BOOT_ID, PARAM_FOLLOW, PARAM_SYSLOG_IDENTIFIER
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
    CONTENT_TYPE_TEXT,
)
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

IDENTIFIER = "identifier"
BOOTID = "bootid"
DEFAULT_RANGE = 100
DEFAULT_LOG_IDENTIFIERS = [
    "NetworkManager",
    "dropbear",
    "hassos-apparmor",
    "hassos-config",
    "hassos-expand",
    "hassos-overlay",
    "hassos-persists",
    "hassos-zram",
    "kernel",
    "os-agent",
    "rauc",
    "systemd",
]

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
    async def list_boots(self, _: web.Request):
        """Return a list of boot IDs."""
        return {
            str(1 + i - len(self.sys_host.logs.boot_ids)): boot_id
            for i, boot_id in enumerate(self.sys_host.logs.boot_ids)
        }

    @api_process
    async def list_identifiers(self, _: web.Request):
        """Return a list of syslog identifiers."""
        return self.sys_host.logs.identifiers

    def _get_boot_id(self, possible_offset: str) -> str:
        """Convert offset into boot ID if required."""
        with suppress(CoerceInvalid):
            offset = vol.Coerce(int)(possible_offset)
            try:
                return self.sys_host.logs.get_boot_id(offset)
            except (ValueError, HostLogError) as err:
                raise APIError() from err
        return possible_offset

    @api_process
    async def advanced_logs(
        self, request: web.Request, identifier: str | None = None, follow: bool = False
    ) -> web.StreamResponse:
        """Return systemd-journald logs."""
        params = {}
        if identifier:
            params[PARAM_SYSLOG_IDENTIFIER] = identifier
        elif IDENTIFIER in request.match_info:
            params[PARAM_SYSLOG_IDENTIFIER] = request.match_info.get(IDENTIFIER)
        else:
            params[PARAM_SYSLOG_IDENTIFIER] = DEFAULT_LOG_IDENTIFIERS

        if BOOTID in request.match_info:
            params[PARAM_BOOT_ID] = self._get_boot_id(request.match_info.get(BOOTID))
        if follow:
            params[PARAM_FOLLOW] = ""

        if ACCEPT in request.headers and request.headers[ACCEPT] not in [
            CONTENT_TYPE_TEXT,
            "*/*",
        ]:
            raise APIError(
                "Invalid content type requested. Only text/plain supported for now."
            )

        if RANGE in request.headers:
            range_header = request.headers.get(RANGE)
        else:
            range_header = f"entries=:-{DEFAULT_RANGE}:"

        async with self.sys_host.logs.journald_logs(
            params=params, range_header=range_header
        ) as resp:
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
