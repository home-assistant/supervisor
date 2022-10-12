"""Logs control for host."""
from __future__ import annotations

from contextlib import asynccontextmanager
import json
import logging
from pathlib import Path

from aiohttp import ClientError, ClientSession, ClientTimeout
from aiohttp.client_reqrep import ClientResponse
from aiohttp.connector import UnixConnector
from aiohttp.hdrs import ACCEPT, RANGE

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ConfigurationFileError, HostLogError, HostNotSupportedError
from ..utils.json import read_json_file
from .const import PARAM_BOOT_ID, PARAM_SYSLOG_IDENTIFIER, LogFormat

_LOGGER: logging.Logger = logging.getLogger(__name__)

# pylint: disable=no-member
SYSLOG_IDENTIFIERS_JSON: Path = (
    Path(__file__).parents[1].joinpath("data/syslog-identifiers.json")
)
# pylint: enable=no-member

SYSTEMD_JOURNAL_GATEWAYD_SOCKET: Path = Path("/run/systemd-journal-gatewayd.sock")

# From systemd catalog for message IDs (`journalctl --dump-catalog``)
# -- b07a249cd024414a82dd00cd181378ff
# Subject: System start-up is now complete
# Defined-By: systemd
BOOT_IDS_QUERY = {"MESSAGE_ID": "b07a249cd024414a82dd00cd181378ff"}


class LogsControl(CoreSysAttributes):
    """Handle systemd-journal logs."""

    def __init__(self, coresys: CoreSys):
        """Initialize host power handling."""
        self.coresys: CoreSys = coresys
        self._profiles: set[str] = set()
        self._boot_ids: list[str] = []
        self._identifiers: list[str] = []
        self._default_identifiers: list[str] = []

    @property
    def available(self) -> bool:
        """Return True if Unix socket to systemd-journal-gatwayd is available."""
        return SYSTEMD_JOURNAL_GATEWAYD_SOCKET.is_socket()

    @property
    def boot_ids(self) -> list[str]:
        """Get boot IDs from oldest to newest."""
        return self._boot_ids

    @property
    def identifiers(self) -> list[str]:
        """Get syslog identifiers."""
        return self._identifiers

    @property
    def default_identifiers(self) -> list[str]:
        """Get default syslog identifiers."""
        return self._default_identifiers

    def get_boot_id(self, offset: int = 0):
        """
        Get ID of a boot by offset.

        Current boot is offset = 0, negative numbers go that many in the past.
        Positive numbers count up from the oldest boot.
        """
        if not self.boot_ids:
            raise HostLogError(
                "Unable to obtain boot IDs from host, check logs for errors"
            )

        offset -= 1
        if offset >= len(self.boot_ids) or abs(offset) > len(self.boot_ids):
            raise ValueError(f"Logs only contain {len(self.boot_ids)} boots")

        return self.boot_ids[offset]

    async def load(self) -> None:
        """Load log control."""
        try:
            self._default_identifiers = read_json_file(SYSLOG_IDENTIFIERS_JSON)
        except ConfigurationFileError:
            _LOGGER.warning(
                "Can't read syslog identifiers json file from %s",
                SYSLOG_IDENTIFIERS_JSON,
            )

        # Build log caches asynchronously
        self.sys_create_task(self.update())

    async def update(self) -> None:
        """Cache boot and identifier information."""
        try:
            async with self.journald_logs(
                path=f"/fields/{PARAM_SYSLOG_IDENTIFIER}",
                timeout=ClientTimeout(total=20),
            ) as resp:
                self._identifiers = (await resp.text()).split("\n")
        except (ClientError, TimeoutError) as err:
            raise HostLogError(
                "Could not get a list of syslog identifiers from systemd-journal-gatewayd",
                _LOGGER.error,
            ) from err

        if self.boot_ids:
            # Doesn't change without a reboot, no reason to query again once cached
            return

        try:
            async with self.journald_logs(
                params=BOOT_IDS_QUERY,
                accept=LogFormat.JSON,
                timeout=ClientTimeout(total=20),
            ) as resp:
                text = await resp.text()
                self._boot_ids = [
                    json.loads(entry)[PARAM_BOOT_ID]
                    for entry in text.split("\n")
                    if entry
                ]
        except (ClientError, TimeoutError) as err:
            raise HostLogError(
                "Could not get a list of boot IDs from systemd-journal-gatewayd",
                _LOGGER.error,
            ) from err

        return

    @asynccontextmanager
    async def journald_logs(
        self,
        path: str = "/entries",
        params: dict[str, str | list[str]] | None = None,
        range_header: str | None = None,
        accept: LogFormat = LogFormat.TEXT,
        timeout: ClientTimeout | None = None,
    ) -> ClientResponse:
        """Get logs from systemd-journal-gatewayd.

        See https://www.freedesktop.org/software/systemd/man/systemd-journal-gatewayd.service.html for params and more info.
        """
        if not self.available:
            raise HostNotSupportedError(
                "No systemd-journal-gatewayd Unix socket available", _LOGGER.error
            )

        async with ClientSession(
            connector=UnixConnector(path="/run/systemd-journal-gatewayd.sock")
        ) as session:
            headers = {ACCEPT: accept.value}
            if range_header:
                headers[RANGE] = range_header
            async with session.get(
                f"http://localhost{path}",
                headers=headers,
                params=params or {},
                timeout=timeout,
            ) as client_response:
                yield client_response
