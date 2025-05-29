"""Logs control for host."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import json
import logging
import os
from pathlib import Path
import re
from typing import Self

from aiohttp import ClientError, ClientSession, ClientTimeout
from aiohttp.client_exceptions import UnixClientConnectorError
from aiohttp.client_reqrep import ClientResponse
from aiohttp.connector import UnixConnector
from aiohttp.hdrs import ACCEPT, RANGE

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    ConfigurationFileError,
    HostLogError,
    HostNotSupportedError,
    HostServiceError,
)
from ..utils.json import read_json_file
from ..utils.systemd_journal import journal_boots_reader
from .const import PARAM_BOOT_ID, PARAM_SYSLOG_IDENTIFIER, LogFormat

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-member
SYSLOG_IDENTIFIERS_JSON: Path = (
    Path(__file__).parents[1].joinpath("data/syslog-identifiers.json")
)
# pylint: enable=no-member

SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX = (1 << 64) - 1

SYSTEMD_JOURNAL_GATEWAYD_SOCKET: Path = Path("/run/systemd-journal-gatewayd.sock")

# From systemd catalog for message IDs (`journalctl --dump-catalog``)
# -- b07a249cd024414a82dd00cd181378ff
# Subject: System start-up is now complete
# Defined-By: systemd
BOOT_IDS_QUERY = {"MESSAGE_ID": "b07a249cd024414a82dd00cd181378ff"}

RE_ENTRIES_HEADER = re.compile(
    r"^entries=(?P<cursor>[^:]*):(?P<num_skip>-?\d+):(?P<num_lines>\d*)$"
)


class LogsControl(CoreSysAttributes):
    """Handle systemd-journal logs."""

    def __init__(self, coresys: CoreSys):
        """Initialize host power handling."""
        self.coresys: CoreSys = coresys
        self._profiles: set[str] = set()
        self._boot_ids: list[str] = []
        self._default_identifiers: list[str] = []
        self._available: bool = False

    async def post_init(self) -> Self:
        """Post init actions that must occur in event loop."""
        self._available = bool(
            os.environ.get("SUPERVISOR_SYSTEMD_JOURNAL_GATEWAYD_URL")
        ) or await self.sys_run_in_executor(SYSTEMD_JOURNAL_GATEWAYD_SOCKET.is_socket)
        return self

    @property
    def available(self) -> bool:
        """Check if systemd-journal-gatwayd is available."""
        return self._available

    @property
    def boot_ids(self) -> list[str]:
        """Get boot IDs from oldest to newest."""
        return self._boot_ids

    @property
    def default_identifiers(self) -> list[str]:
        """Get default syslog identifiers."""
        return self._default_identifiers

    async def load(self) -> None:
        """Load log control."""
        try:
            self._default_identifiers = await self.sys_run_in_executor(
                read_json_file, SYSLOG_IDENTIFIERS_JSON
            )
        except ConfigurationFileError:
            _LOGGER.warning(
                "Can't read syslog identifiers json file from %s",
                SYSLOG_IDENTIFIERS_JSON,
            )

    async def get_boot_id(self, offset: int = 0) -> str:
        """Get ID of a boot by offset.

        Current boot is offset = 0, negative numbers go that many in the past.
        Positive numbers count up from the oldest boot.
        """
        boot_ids = await self.get_boot_ids()
        offset -= 1
        if offset >= len(boot_ids) or abs(offset) > len(boot_ids):
            raise ValueError(f"Logs only contain {len(boot_ids)} boots")

        return boot_ids[offset]

    async def _get_boot_ids_legacy(self) -> list[str]:
        """Get boots IDs using suboptimal method where /boots is not available."""
        try:
            async with self.journald_logs(
                params=BOOT_IDS_QUERY,
                accept=LogFormat.JSON,
                timeout=ClientTimeout(total=20),
            ) as resp:
                text = await resp.text()
        except (ClientError, TimeoutError) as err:
            raise HostLogError(
                "Could not get a list of boot IDs from systemd-journal-gatewayd",
                _LOGGER.error,
            ) from err

        # Get the oldest log entry. This makes sure that its ID is included
        # if the start of the oldest boot was rotated out of the journal.
        try:
            async with self.journald_logs(
                range_header="entries=:0:1",
                accept=LogFormat.JSON,
                timeout=ClientTimeout(total=20),
            ) as resp:
                text = await resp.text() + text
        except (ClientError, TimeoutError) as err:
            raise HostLogError(
                "Could not get a list of boot IDs from systemd-journal-gatewayd",
                _LOGGER.error,
            ) from err

        _boot_ids = []
        for entry in text.split("\n"):
            if entry and (boot_id := json.loads(entry)[PARAM_BOOT_ID]) not in _boot_ids:
                _boot_ids.append(boot_id)

        return _boot_ids

    async def _get_boot_ids_native(self):
        """Get boot IDs using /boots endpoint."""
        try:
            async with self.journald_logs(
                path="/boots",
                accept=LogFormat.JSON_SEQ,
                timeout=ClientTimeout(total=20),
            ) as resp:
                if resp.status != 200:
                    raise HostLogError(
                        f"Got HTTP {resp.status} from /boots.",
                        _LOGGER.debug,
                    )
                # Don't rely solely on the order of boots in the response,
                # sort the boots by index returned in the response.
                boot_id_tuples = [boot async for boot in journal_boots_reader(resp)]
                return [
                    boot_id for _, boot_id in sorted(boot_id_tuples, key=lambda x: x[0])
                ]
        except (ClientError, TimeoutError) as err:
            raise HostLogError(
                "Could not get a list of boot IDs from systemd-journal-gatewayd",
                _LOGGER.error,
            ) from err

    async def get_boot_ids(self) -> list[str]:
        """Get boot IDs from oldest to newest."""
        if self._boot_ids:
            # Doesn't change without a reboot, no reason to query again once cached
            return self._boot_ids

        try:
            self._boot_ids = await self._get_boot_ids_native()
        except HostLogError:
            _LOGGER.info(
                "Could not get /boots from systemd-journal-gatewayd, using fallback."
            )
            self._boot_ids = await self._get_boot_ids_legacy()

        return self._boot_ids

    async def get_identifiers(self) -> list[str]:
        """Get syslog identifiers."""
        try:
            async with self.journald_logs(
                path=f"/fields/{PARAM_SYSLOG_IDENTIFIER}",
                timeout=ClientTimeout(total=20),
            ) as resp:
                return [i for i in (await resp.text()).split("\n") if i]
        except (ClientError, TimeoutError) as err:
            raise HostLogError(
                "Could not get a list of syslog identifiers from systemd-journal-gatewayd",
                _LOGGER.error,
            ) from err

    @asynccontextmanager
    async def journald_logs(
        self,
        path: str = "/entries",
        params: dict[str, str | list[str]] | None = None,
        range_header: str | None = None,
        accept: LogFormat = LogFormat.TEXT,
        timeout: ClientTimeout | None = None,
    ) -> AsyncGenerator[ClientResponse]:
        """Get logs from systemd-journal-gatewayd.

        See https://www.freedesktop.org/software/systemd/man/systemd-journal-gatewayd.service.html for params and more info.
        """
        if not self.available:
            raise HostNotSupportedError(
                "No systemd-journal-gatewayd Unix socket available", _LOGGER.error
            )

        try:
            if base_url := os.environ.get("SUPERVISOR_SYSTEMD_JOURNAL_GATEWAYD_URL"):
                connector = None
            else:
                base_url = "http://localhost/"
                connector = UnixConnector(path=str(SYSTEMD_JOURNAL_GATEWAYD_SOCKET))
            async with ClientSession(base_url=base_url, connector=connector) as session:
                headers = {ACCEPT: accept}
                if range_header:
                    if range_header.endswith(":"):
                        # Make sure that num_entries is always set - before Systemd v256 it was
                        # possible to omit it, which made sense when the "follow" option was used,
                        # but this syntax is now invalid and triggers HTTP 400.
                        # See: https://github.com/systemd/systemd/issues/37172
                        if not (matches := re.match(RE_ENTRIES_HEADER, range_header)):
                            raise HostNotSupportedError(
                                f"Invalid range header: {range_header}"
                            )
                        range_header = f"entries={matches.group('cursor')}:{matches.group('num_skip')}:{SYSTEMD_JOURNAL_GATEWAYD_LINES_MAX}"
                    headers[RANGE] = range_header
                async with session.get(
                    f"{path}",
                    headers=headers,
                    params=params or {},
                    timeout=timeout,
                ) as client_response:
                    yield client_response
        except UnixClientConnectorError as ex:
            raise HostServiceError(
                "Unable to connect to systemd-journal-gatewayd", _LOGGER.error
            ) from ex
