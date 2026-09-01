"""Init file for Supervisor host RESTful API."""

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import json
import logging
from typing import Any

from aiohttp import (
    ClientConnectionResetError,
    ClientError,
    ClientPayloadError,
    ClientTimeout,
    web,
)
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
from ..exceptions import (
    APIDBMigrationInProgress,
    APIError,
    HostContainerLogEpochError,
    HostLogError,
    MountNotFound,
    MountUsageNotMountedError,
    MountUsageReadError,
    MountUsageTimeoutError,
)
from ..host.const import (
    PARAM_BOOT_ID,
    PARAM_FOLLOW,
    PARAM_SYSLOG_IDENTIFIER,
    LogFormat,
    LogFormatter,
)
from ..host.logs import SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX
from ..mounts.mount import Mount
from ..utils.systemd_journal import journal_logs_reader
from .const import (
    ATTR_AGENT_VERSION,
    ATTR_APPARMOR_VERSION,
    ATTR_BOOT_TIMESTAMP,
    ATTR_BOOTS,
    ATTR_BROADCAST_LLMNR,
    ATTR_BROADCAST_MDNS,
    ATTR_CHILDREN,
    ATTR_DT_SYNCHRONIZED,
    ATTR_DT_UTC,
    ATTR_FORCE,
    ATTR_IDENTIFIERS,
    ATTR_LLMNR_HOSTNAME,
    ATTR_MAX_DEPTH,
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

DISK = "disk"

# Reserved disk target naming the system disk. Takes precedence over a mount of
# the same name, which the mount name pattern permits.
DISK_TARGET_SYSTEM = "default"

# The system disk lists labeled known paths at depth 1. A mount has no such
# labels, so depth 1 would walk its whole tree to report a single total; mounts
# therefore default to totals only and opt in to a breakdown explicitly.
DISK_USAGE_MAX_DEPTH_SYSTEM = 1
DISK_USAGE_MAX_DEPTH_MOUNT = 0

# How long a caller waits on a mount usage probe before getting a timeout
# error. Bounds only the wait, never the probe: the probe keeps running so
# later requests join it instead of stacking executor threads against the
# same slow mount. Deliberately longer than any protocol timeout, since a
# probe of an unreachable network mount is expected to run to the kernel's
# own bound.
MOUNT_USAGE_TIMEOUT = 60

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

    def __init__(self) -> None:
        """Initialize host API handler."""
        # In-flight mount usage probes, keyed by (mount name, max depth). A probe
        # of an unreachable mount blocks until the kernel gives up, so callers
        # asking for the same thing await the pending probe rather than parking
        # another executor thread on identical work. Mounts only: the system disk
        # keeps its existing per-request behavior.
        self._mount_usage_probes: dict[
            tuple[str, int], asyncio.Task[dict[str, Any]]
        ] = {}

    @staticmethod
    def _legacy_disk_usage_ids_for_v1(data: dict[str, Any]) -> dict[str, Any]:
        """Translate app terminology IDs to legacy addon IDs for v1 responses."""
        legacy_id_map = {
            "apps_data": "addons_data",
            "apps_config": "addons_config",
        }

        children = data.get("children", [])
        for child in children:
            if (child_id := child.get("id")) in legacy_id_map:
                child["id"] = legacy_id_map[child_id]

        return data

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
    async def info(self, request: web.Request) -> dict[str, Any]:
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
    async def options(self, request: web.Request) -> None:
        """Edit host settings."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        # hostname
        if ATTR_HOSTNAME in body:
            await asyncio.shield(
                self.sys_host.control.set_hostname(body[ATTR_HOSTNAME])
            )

    @api_process
    async def reboot(self, request: web.Request) -> None:
        """Reboot host."""
        body = await api_validate(SCHEMA_SHUTDOWN, request)
        await self._check_ha_offline_migration(force=body[ATTR_FORCE])

        return await asyncio.shield(self.sys_host.control.reboot())

    @api_process
    async def shutdown(self, request: web.Request) -> None:
        """Poweroff host."""
        body = await api_validate(SCHEMA_SHUTDOWN, request)
        await self._check_ha_offline_migration(force=body[ATTR_FORCE])

        return await asyncio.shield(self.sys_host.control.shutdown())

    @api_process
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload host data."""
        return asyncio.shield(self.sys_host.reload())

    @api_process
    async def services(self, request: web.Request) -> dict[str, Any]:
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
    async def list_boots(self, _: web.Request) -> dict[str, Any]:
        """Return a list of boot IDs."""
        boot_ids = await self.sys_host.logs.get_boot_ids()
        return {
            ATTR_BOOTS: {
                str(1 + i - len(boot_ids)): boot_id
                for i, boot_id in enumerate(boot_ids)
            }
        }

    @api_process
    async def list_identifiers(self, _: web.Request) -> dict[str, list[str]]:
        """Return a list of syslog identifiers."""
        return {ATTR_IDENTIFIERS: await self.sys_host.logs.get_identifiers()}

    async def _get_boot_id(self, possible_offset: str) -> str:
        """Convert offset into boot ID if required."""
        with suppress(CoerceInvalid):
            offset = vol.Coerce(int)(possible_offset)
            try:
                return await self.sys_host.logs.get_boot_id(offset)
            except (ValueError, HostLogError) as err:
                raise APIError from err
        return possible_offset

    async def advanced_logs_handler(
        self,
        request: web.Request,
        identifier: str | list[str] | None = None,
        follow: bool = False,
        latest: bool = False,
        no_colors: bool = False,
        default_verbose: bool = False,
    ) -> web.StreamResponse:
        """Return systemd-journald logs."""
        log_formatter = LogFormatter.VERBOSE if default_verbose else LogFormatter.PLAIN
        params: dict[str, Any] = {}
        if identifier:
            params[PARAM_SYSLOG_IDENTIFIER] = identifier
        elif IDENTIFIER in request.match_info:
            params[PARAM_SYSLOG_IDENTIFIER] = request.match_info[IDENTIFIER]
        else:
            params[PARAM_SYSLOG_IDENTIFIER] = self.sys_host.logs.default_identifiers

        if BOOTID in request.match_info:
            params[PARAM_BOOT_ID] = await self._get_boot_id(request.match_info[BOOTID])
        if follow:
            params[PARAM_FOLLOW] = ""

        if latest:
            if not identifier:
                raise APIError(
                    "Latest logs can only be fetched for a specific identifier."
                )

            epoch = await self._get_container_last_epoch(identifier)
            params["CONTAINER_LOG_EPOCH"] = epoch

        accept_header = request.headers.get(ACCEPT)

        if accept_header and accept_header not in [
            CONTENT_TYPE_TEXT,
            CONTENT_TYPE_X_LOG,
            "*/*",
        ]:
            raise APIError(
                "Invalid content type requested. Only text/plain and text/x-log "
                "supported for now."
            )

        if "verbose" in request.query or accept_header == CONTENT_TYPE_X_LOG:
            log_formatter = LogFormatter.VERBOSE

        if "no_colors" in request.query:
            no_colors = True

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
        elif latest:
            range_header = f"entries=:0:{SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX}"
        elif RANGE in request.headers:
            range_header = request.headers[RANGE]
        else:
            range_header = f"entries=:-{DEFAULT_LINES - 1}:{SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX if follow else DEFAULT_LINES}"

        async with self.sys_host.logs.journald_logs(
            params=params, range_header=range_header, accept=LogFormat.JOURNAL
        ) as resp:
            response = web.StreamResponse()
            response.content_type = CONTENT_TYPE_TEXT
            headers_returned = False
            try:
                async for cursor, line in journal_logs_reader(
                    resp, log_formatter, no_colors
                ):
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
                # If the stream to the client already started, an error response
                # can no longer be sent, so just end the stream. This happens
                # e.g. when systemd-journal-gatewayd is stopped on host shutdown
                # while a client is following the logs.
                if not headers_returned:
                    raise APIError(
                        "Connection reset when trying to fetch data from systemd-journald."
                    ) from ex
                _LOGGER.debug(
                    "%s raised when reading journal logs: %s",
                    type(ex).__name__,
                    ex,
                )
            return response

    @api_process_raw(CONTENT_TYPE_TEXT, error_type=CONTENT_TYPE_TEXT)
    async def advanced_logs(
        self,
        request: web.Request,
        identifier: str | list[str] | None = None,
        follow: bool = False,
        latest: bool = False,
        no_colors: bool = False,
        default_verbose: bool = False,
    ) -> web.StreamResponse:
        """Return systemd-journald logs. Wrapped as standard API handler."""
        return await self.advanced_logs_handler(
            request, identifier, follow, latest, no_colors, default_verbose
        )

    @api_process
    async def disk_usage(self, request: web.Request) -> dict[str, Any]:
        """Return a breakdown of storage usage for the system disk or a mount."""
        return await self._disk_usage_data(request)

    async def _disk_usage_data(self, request: web.Request) -> dict[str, Any]:
        """Build disk usage response data for the requested disk."""
        target = request.match_info.get(DISK, DISK_TARGET_SYSTEM)
        if target == DISK_TARGET_SYSTEM:
            return await self._system_disk_usage_data(request)

        return await self._mount_disk_usage_data(request, target)

    @staticmethod
    def _requested_max_depth(request: web.Request, default: int) -> int:
        """Return the requested max depth, falling back to default if unusable."""
        max_depth = request.query.get(ATTR_MAX_DEPTH, default)
        try:
            return int(max_depth)
        except ValueError:
            return default

    async def _system_disk_usage_data(self, request: web.Request) -> dict[str, Any]:
        """Build disk usage response data for the system disk."""
        max_depth = self._requested_max_depth(request, DISK_USAGE_MAX_DEPTH_SYSTEM)

        disk = self.sys_hardware.disk

        total, _, free = await self.sys_run_in_executor(
            disk.disk_usage, self.sys_config.path_supervisor
        )

        # Calculate used by subtracting free makes sure we include reserved space
        # in used space reporting.
        used = total - free

        known_paths = await self.sys_run_in_executor(
            disk.get_dir_sizes,
            {
                "apps_data": self.sys_config.path_apps_data,
                "apps_config": self.sys_config.path_app_configs,
                "media": self.sys_config.path_media,
                "share": self.sys_config.path_share,
                "backup": self.sys_config.path_backup,
                "ssl": self.sys_config.path_ssl,
                "homeassistant": self.sys_config.path_homeassistant,
            },
            max_depth,
        )
        return {
            # this can be the disk/partition ID in the future
            "id": "root",
            "label": "Root",
            "total_bytes": total,
            "used_bytes": used,
            ATTR_CHILDREN: [
                {
                    "id": "system",
                    "label": "System",
                    "used_bytes": used
                    - sum(path["used_bytes"] for path in known_paths),
                },
                *known_paths,
            ],
        }

    async def _mount_disk_usage_data(
        self, request: web.Request, name: str
    ) -> dict[str, Any]:
        """Build disk usage response data for a supervisor mount."""
        if name not in self.sys_mounts:
            raise MountNotFound(name=name)

        mount = self.sys_mounts.get(name)
        # Don't use cached mount state — it can be 15 minutes stale.
        # The probe below activates a dormant automount if needed.

        max_depth = self._requested_max_depth(request, DISK_USAGE_MAX_DEPTH_MOUNT)
        # All depths below 2 give totals only; normalize so concurrent callers
        # share one probe regardless of the requested depth.
        if max_depth < 2:
            max_depth = DISK_USAGE_MAX_DEPTH_MOUNT
        return await self._mount_usage(mount, max_depth)

    async def _mount_usage(self, mount: Mount, max_depth: int) -> dict[str, Any]:
        """Return usage for a mount, joining an identical probe already running."""
        key = (mount.name, max_depth)
        if (probe := self._mount_usage_probes.get(key)) is None:

            def _probe_done(task: asyncio.Task[dict[str, Any]]) -> None:
                # Drop the entry so a failed probe cannot poison later requests
                # and a stale result is never served. Guarded by identity so a
                # replacement probe registered under the same key can never be
                # evicted by a stale callback.
                if self._mount_usage_probes.get(key) is task:
                    del self._mount_usage_probes[key]

                # Retrieve the failure even when nobody is left to receive it. A
                # probe outlives the caller that started it, so a client giving up
                # on an unreachable mount leaves a probe that still fails later;
                # an unretrieved task exception would then be reported as though
                # supervisor had faulted rather than a mount having not answered.
                if not task.cancelled() and (err := task.exception()) is not None:
                    _LOGGER.debug(
                        "Storage usage probe for mount %s failed: %s", mount.name, err
                    )

            probe = self.sys_create_task(self._mount_usage_data(mount, max_depth))
            self._mount_usage_probes[key] = probe
            probe.add_done_callback(_probe_done)

        # Waiting on the probe rather than awaiting it directly keeps a client
        # that disconnects from cancelling work other callers share.
        #
        # Deliberately not asyncio.shield: it achieves the same isolation, but
        # once its own await is cancelled it attaches a handler that pushes any
        # failure through the loop exception handler as "<error> exception in
        # shielded future". An unreachable mount is the case this endpoint exists
        # to report on, so that would log a traceback for an expected outcome
        # every time a user navigated away from a spinner.
        #
        # The timeout belongs to this wait, not to the probe. A probe killed by
        # its own timeout would be popped from the registry while its executor
        # thread stays parked in the kernel, so the next request would stack a
        # fresh thread against the same unresponsive mount - the exact pile-up
        # the registry exists to prevent. Timing out only the wait keeps the
        # probe and its entry alive: slow callers get their error, later
        # callers join the same probe, and the one thread is released by the
        # kernel exactly once. Reachable legitimately via a long depth walk of
        # a big share, not only via a dead server.
        done, _ = await asyncio.wait({probe}, timeout=MOUNT_USAGE_TIMEOUT)
        if not done:
            raise MountUsageTimeoutError(name=mount.name)
        return probe.result()

    async def _mount_usage_data(self, mount: Mount, max_depth: int) -> dict[str, Any]:
        """Probe a mount for its storage usage.

        Runs to the kernel's own bound rather than a timeout of its own: the
        frontend shows a loader per mount and a real answer is worth waiting
        for. Callers bound their wait without cancelling this probe.
        """
        disk = self.sys_hardware.disk

        try:
            usage = await self.sys_run_in_executor(
                disk.disk_usage_for_mount, mount.local_where
            )

            children: list[dict[str, Any]] = []
            # The walker recurses regardless of max_depth and only emits
            # children when max_depth exceeds 1, so it is skipped whenever it
            # could not produce output - otherwise a request would walk the
            # whole mount for nothing. Depth 1 emits nothing here because for
            # the system disk that level is the labeled known paths, which
            # come from get_dir_sizes rather than this walker, and a mount
            # has no equivalent layer. Read errors from the walk stay this
            # mount's problem: reporting them to the resolution center would
            # mark the whole system unhealthy over an unreachable server.
            if usage is not None and max_depth > 1:
                structure = await self.sys_run_in_executor(
                    disk.get_dir_structure_sizes,
                    mount.local_where,
                    max_depth,
                    check_oserror=False,
                )
                children = structure.get(ATTR_CHILDREN, [])
        except OSError as err:
            raise MountUsageReadError(name=mount.name, reason=str(err)) from err

        if usage is None:
            # Not a mount point. The probe would already have activated a
            # dormant automount, so this is a plain directory — don't report
            # the host data disk's numbers as this mount.
            raise MountUsageNotMountedError(name=mount.name)

        total, _, free = usage
        # Same reserved-space convention as the system disk
        used = total - free

        data: dict[str, Any] = {
            "id": mount.name,
            "label": mount.name,
            "total_bytes": total,
            "used_bytes": used,
        }
        # Omitted rather than empty, matching every other node in the tree
        if children:
            # Keep every node's children summing to its used_bytes, so a mount
            # breaks down like anything else in the tree. Files directly at the
            # mount root, reserved space, and anything the walk could not stat
            # all land here.
            walked = sum(child["used_bytes"] for child in children)
            remainder = used - walked
            if remainder > 0:
                children = [
                    *children,
                    {"id": "other", "label": "Other", "used_bytes": remainder},
                ]
            elif remainder < 0:
                # Walk raced a deletion; drop the breakdown rather than serve
                # children summing past their parent.
                _LOGGER.warning(
                    "Directory sizes of mount %s (%d bytes) exceed its reported "
                    "usage (%d bytes), likely because files changed during the "
                    "scan. Omitting the breakdown for this request",
                    mount.name,
                    walked,
                    used,
                )
                children = []

        if children:
            data[ATTR_CHILDREN] = children

        return data

    @api_process
    async def disk_usage_v1(self, request: web.Request) -> dict[str, Any]:
        """Return disk usage with legacy addon IDs for v1 compatibility."""
        data = await self._disk_usage_data(request)

        # Legacy ids exist only in the system disk's labeled layer. Mount
        # children are real directory names, and the shared probe result
        # must not be mutated in place.
        if request.match_info.get(DISK, DISK_TARGET_SYSTEM) == DISK_TARGET_SYSTEM:
            data = self._legacy_disk_usage_ids_for_v1(data)

        return data

    async def _get_container_last_epoch(self, identifier: str | list[str]) -> str:
        """Get Docker's internal log epoch of the latest log entry for given identifier(s)."""
        identifiers = [identifier] if isinstance(identifier, str) else identifier

        try:
            async with self.sys_host.logs.journald_logs(
                params={"CONTAINER_NAME": identifier},
                range_header="entries=:-1:2",  # -1 = next to the last entry
                accept=LogFormat.JSON,
                timeout=ClientTimeout(total=10),
            ) as resp:
                text = await resp.text()
        except (ClientError, TimeoutError) as err:
            _LOGGER.error(
                "Could not get last container epoch from systemd-journal-gatewayd for identifiers: %s",
                ", ".join(identifiers),
            )
            raise HostContainerLogEpochError(
                identifiers=identifiers,
            ) from err

        try:
            return json.loads(text.strip().split("\n")[-1])["CONTAINER_LOG_EPOCH"]
        except (json.JSONDecodeError, KeyError, IndexError) as err:
            _LOGGER.error(
                "Failed to parse CONTAINER_LOG_EPOCH from systemd-journald response for identifiers %s: %s",
                ", ".join(identifiers),
                text,
            )
            raise HostContainerLogEpochError(identifiers=identifiers) from err
