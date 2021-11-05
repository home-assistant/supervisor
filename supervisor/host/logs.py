"""Logs control for host."""
from __future__ import annotations

from contextlib import asynccontextmanager
import logging
from pathlib import Path
from typing import AsyncIterator

from aiohttp import ClientSession
from aiohttp.client_reqrep import ClientResponse
from aiohttp.connector import UnixConnector
from aiohttp.hdrs import ACCEPT, RANGE

from supervisor.coresys import CoreSys, CoreSysAttributes
from supervisor.exceptions import HostNotSupportedError

_LOGGER: logging.Logger = logging.getLogger(__name__)

SYSTEMD_JOURNAL_GATEWAYD_SOCKET: Path = Path("/run/systemd-journal-gatewayd.sock")


class LogsControl(CoreSysAttributes):
    """Handle systemd-journal logs."""

    def __init__(self, coresys: CoreSys):
        """Initialize host power handling."""
        self.coresys: CoreSys = coresys
        self._profiles: set[str] = set()

    @property
    def available(self) -> bool:
        """Return True if Unix socket to systemd-journal-gatwayd is available."""
        return SYSTEMD_JOURNAL_GATEWAYD_SOCKET.is_socket()

    @asynccontextmanager
    async def journald_logs(self, params, range) -> AsyncIterator[ClientResponse]:
        """Get logs from systemd-journal-gatewayd."""

        if not self.available:
            raise HostNotSupportedError(
                "No systemd-journal-gatewayd Unix socket available", _LOGGER.error
            )

        conn = UnixConnector(path="/run/systemd-journal-gatewayd.sock")

        async with ClientSession(connector=conn) as session:
            headers = {ACCEPT: "text/plain"}
            if range:
                headers[RANGE] = range
            async with session.get(
                "http://localhost/entries",
                headers=headers,
                params=params,
                timeout=None,
            ) as client_response:
                yield client_response
                return
