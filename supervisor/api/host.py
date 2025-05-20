"""Init file for Supervisor host RESTful API."""

import asyncio
from contextlib import suppress
import logging
from typing import Any

from aiohttp import ClientConnectionResetError, ClientPayloadError, web
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
from ..exceptions import APIDBMigrationInProgress, APIError, HostLogError
from ..host.const import (
    PARAM_BOOT_ID,
    PARAM_FOLLOW,
    PARAM_SYSLOG_IDENTIFIER,
    LogFormat,
    LogFormatter,
)
from ..host.logs import SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX
from ..utils.systemd_journal import journal_logs_reader
from .const import (
    ATTR_AGENT_VERSION,
    ATTR_APPARMOR_VERSION,
    ATTR_BOOT_TIMESTAMP,
    ATTR_BOOTS,
    ATTR_BROADCAST_LLMNR,
    ATTR_BROADCAST_MDNS,
    ATTR_DT_SYNCHRONIZED,
    ATTR_DT_UTC,
    ATTR_FORCE,
    ATTR_IDENTIFIERS,
    ATTR_LLMNR_HOSTNAME,
    ATTR_STARTUP_TIME,
    ATTR_USE_NTP,
    ATTR_VIRTUALIZATION,
    CONTENT_TYPE_TEXT,
    CONTENT_TYPE_X_LOG,
)
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

IDENTIFIER = "identifier"
BOOTID = "bootid"
DEFAULT_LINES = 100

SCHEMA_OPTIONS = vol.Schema({vol.Optional(ATTR_HOSTNAME): str})

# pylint: disable=no-value-for-parameter
SCHEMA_SHUTDOWN = vol.Schema(
    {
        vol.Optional(ATTR_FORCE, default=False): vol.Boolean(),
    }
)
# pylint: enable=no-value-for-parameter


class APIHost(CoreSysAttributes):
    """Handle RESTful API for host functions."""

    async def _check_ha_offline_migration(self, force: bool) -> None:
        """Check if HA has an offline migration in progress and raise if not forced."""
        if (
            not force
            and (state := await self.sys_homeassistant.api.get_api_state())
            and state.offline_db_migration
        ):
            raise APIDBMigrationInProgress(
                "Home Assistant offline database migration in progress, please wait until complete before shutting down host"
            )

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_AGENT_VERSION: self.sys_dbus.agent.version,
            ATTR_APPARMOR_VERSION: self.sys_host.apparmor.version,
            ATTR_CHASSIS: self.sys_host.info.chassis,
            ATTR_VIRTUALIZATION: self.sys_host.info.virtualization,
            ATTR_CPE: self.sys_host.info.cpe,
            ATTR_DEPLOYMENT: self.sys_host.info.deployment,
            ATTR_DISK_FREE: await self.sys_host.info.free_space(),
            ATTR_DISK_TOTAL: await self.sys_host.info.total_space(),
            ATTR_DISK_USED: await self.sys_host.info.used_space(),
            ATTR_DISK_LIFE_TIME: await self.sys_host.info.disk_life_time(),
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
    async def reboot(self, request):
        """Reboot host."""
        body = await api_validate(SCHEMA_SHUTDOWN, request)
        await self._check_ha_offline_migration(force=body[ATTR_FORCE])

        return await asyncio.shield(self.sys_host.control.reboot())

    @api_process
    async def shutdown(self, request):
        """Poweroff host."""
        body = await api_validate(SCHEMA_SHUTDOWN, request)
        await self._check_ha_offline_migration(force=body[ATTR_FORCE])

        return await asyncio.shield(self.sys_host.control.shutdown())

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
        boot_ids = await self.sys_host.logs.get_boot_ids()
        return {
            ATTR_BOOTS: {
                str(1 + i - len(boot_ids)): boot_id
                for i, boot_id in enumerate(boot_ids)
            }
        }

    @api_process
    async def list_identifiers(self, _: web.Request):
        """Return a list of syslog identifiers."""
        return {ATTR_IDENTIFIERS: await self.sys_host.logs.get_identifiers()}

    async def _get_boot_id(self, possible_offset: str) -> str:
        """Convert offset into boot ID if required."""
        with suppress(CoerceInvalid):
            offset = vol.Coerce(int)(possible_offset)
            try:
                return await self.sys_host.logs.get_boot_id(offset)
            except (ValueError, HostLogError) as err:
                raise APIError() from err
        return possible_offset

    async def advanced_logs_handler(
        self, request: web.Request, identifier: str | None = None, follow: bool = False
    ) -> web.StreamResponse:
        """Return systemd-journald logs."""
        log_formatter = LogFormatter.PLAIN
        params: dict[str, Any] = {}
        if identifier:
            params[PARAM_SYSLOG_IDENTIFIER] = identifier
        elif IDENTIFIER in request.match_info:
            params[PARAM_SYSLOG_IDENTIFIER] = request.match_info[IDENTIFIER]
        else:
            params[PARAM_SYSLOG_IDENTIFIER] = self.sys_host.logs.default_identifiers
            # host logs should be always verbose, no matter what Accept header is used
            log_formatter = LogFormatter.VERBOSE

        if BOOTID in request.match_info:
            params[PARAM_BOOT_ID] = await self._get_boot_id(request.match_info[BOOTID])
        if follow:
            params[PARAM_FOLLOW] = ""

        if ACCEPT in request.headers and request.headers[ACCEPT] not in [
            CONTENT_TYPE_TEXT,
            CONTENT_TYPE_X_LOG,
            "*/*",
        ]:
            raise APIError(
                "Invalid content type requested. Only text/plain and text/x-log "
                "supported for now."
            )

        if "verbose" in request.query or request.headers[ACCEPT] == CONTENT_TYPE_X_LOG:
            log_formatter = LogFormatter.VERBOSE

        if "lines" in request.query:
            lines = request.query.get("lines", DEFAULT_LINES)
            try:
                lines = int(lines)
            except ValueError:
                # If the user passed a non-integer value, just use the default instead of error.
                lines = DEFAULT_LINES
            finally:
                # We can't use the entries= Range header syntax to refer to the last 1 line,
                # and passing 1 to the calculation below would return the 1st line of the logs
                # instead. Since this is really an edge case that doesn't matter much, we'll just
                # return 2 lines at minimum.
                lines = max(2, lines)
            # entries=cursor[[:num_skip]:num_entries]
            range_header = f"entries=:-{lines - 1}:{SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX if follow else lines}"
        elif RANGE in request.headers:
            range_header = request.headers[RANGE]
        else:
            range_header = f"entries=:-{DEFAULT_LINES - 1}:{SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX if follow else DEFAULT_LINES}"

        async with self.sys_host.logs.journald_logs(
            params=params, range_header=range_header, accept=LogFormat.JOURNAL
        ) as resp:
            try:
                response = web.StreamResponse()
                response.content_type = CONTENT_TYPE_TEXT
                headers_returned = False
                async for cursor, line in journal_logs_reader(resp, log_formatter):
                    try:
                        if not headers_returned:
                            if cursor:
                                response.headers["X-First-Cursor"] = cursor
                            response.headers["X-Accel-Buffering"] = "no"
                            await response.prepare(request)
                            headers_returned = True
                        await response.write(line.encode("utf-8") + b"\n")
                    except ClientConnectionResetError as err:
                        # When client closes the connection while reading busy logs, we
                        # sometimes get this exception. It should be safe to ignore it.
                        _LOGGER.debug(
                            "ClientConnectionResetError raised when returning journal logs: %s",
                            err,
                        )
                        break
                    except ConnectionError as err:
                        _LOGGER.warning(
                            "%s raised when returning journal logs: %s",
                            type(err).__name__,
                            err,
                        )
                        break
            except (ConnectionResetError, ClientPayloadError) as ex:
                # ClientPayloadError is most likely caused by the closing the connection
                raise APIError(
                    "Connection reset when trying to fetch data from systemd-journald."
                ) from ex
            return response

    @api_process_raw(CONTENT_TYPE_TEXT, error_type=CONTENT_TYPE_TEXT)
    async def advanced_logs(
        self, request: web.Request, identifier: str | None = None, follow: bool = False
    ) -> web.StreamResponse:
        """Return systemd-journald logs. Wrapped as standard API handler."""
        return await self.advanced_logs_handler(request, identifier, follow)
