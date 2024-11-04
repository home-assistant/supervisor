"""Test host logs control."""

import asyncio
from unittest.mock import MagicMock, PropertyMock, patch

from aiohttp.client_exceptions import UnixClientConnectorError
from aiohttp.client_reqrep import ConnectionKey
import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostNotSupportedError, HostServiceError
from supervisor.host.const import LogFormatter
from supervisor.host.logs import LogsControl
from supervisor.utils.systemd_journal import journal_logs_reader

from tests.common import load_fixture

TEST_BOOT_IDS = [
    "b2aca10d5ca54fb1b6fb35c85a0efca9",
    "b1c386a144fd44db8f855d7e907256f8",
]


async def test_load(coresys: CoreSys):
    """Test load."""
    assert coresys.host.logs.default_identifiers == []

    await coresys.host.logs.load()
    assert coresys.host.logs.boot_ids == []

    # File is quite large so just check it loaded
    for identifier in ["kernel", "os-agent", "systemd"]:
        assert identifier in coresys.host.logs.default_identifiers


async def test_logs(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting logs and errors."""
    assert coresys.host.logs.available is True

    journald_gateway.content.feed_data(
        load_fixture("logs_export_host.txt").encode("utf-8")
    )
    journald_gateway.content.feed_eof()

    async with coresys.host.logs.journald_logs() as resp:
        cursor, line = await anext(
            journal_logs_reader(resp, log_formatter=LogFormatter.VERBOSE)
        )
        assert (
            cursor
            == "s=83fee99ca0c3466db5fc120d52ca7dd8;i=203f2ce;b=f5a5c442fa6548cf97474d2d57c920b3;m=3191a3c620;t=612ccd299e7af;x=8675b540119d10bb"
        )
        assert (
            line
            == "2024-03-04 02:52:56.193 homeassistant systemd[1]: Started Hostname Service."
        )

    with (
        patch.object(LogsControl, "available", new=PropertyMock(return_value=False)),
        pytest.raises(HostNotSupportedError),
    ):
        async with coresys.host.logs.journald_logs():
            pass


async def test_logs_coloured(coresys: CoreSys, journald_gateway: MagicMock):
    """Test ANSI control sequences being preserved in binary messages."""
    journald_gateway.content.feed_data(
        load_fixture("logs_export_supervisor.txt").encode("utf-8")
    )
    journald_gateway.content.feed_eof()

    async with coresys.host.logs.journald_logs() as resp:
        cursor, line = await anext(journal_logs_reader(resp))
        assert (
            cursor
            == "s=83fee99ca0c3466db5fc120d52ca7dd8;i=2049389;b=f5a5c442fa6548cf97474d2d57c920b3;m=4263828e8c;t=612dda478b01b;x=9ae12394c9326930"
        )
        assert (
            line
            == "\x1b[32m24-03-04 23:56:56 INFO (MainThread) [__main__] Closing Supervisor\x1b[0m"
        )


async def test_boot_ids(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting boot ids."""
    journald_gateway.content.feed_data(
        load_fixture("logs_boot_ids.txt").encode("utf-8")
    )
    journald_gateway.content.feed_eof()

    assert await coresys.host.logs.get_boot_ids() == TEST_BOOT_IDS

    # Boot ID query should not be run again, mock a failure for it to ensure
    journald_gateway.get.side_effect = TimeoutError()
    assert await coresys.host.logs.get_boot_ids() == TEST_BOOT_IDS

    assert await coresys.host.logs.get_boot_id(0) == "b1c386a144fd44db8f855d7e907256f8"

    # -1 is previous boot. We have 2 boots so -2 is too far
    assert await coresys.host.logs.get_boot_id(-1) == "b2aca10d5ca54fb1b6fb35c85a0efca9"
    with pytest.raises(ValueError):
        await coresys.host.logs.get_boot_id(-2)

    # 1 is oldest boot and count up from there. We have 2 boots so 3 is too far
    assert await coresys.host.logs.get_boot_id(1) == "b2aca10d5ca54fb1b6fb35c85a0efca9"
    assert await coresys.host.logs.get_boot_id(2) == "b1c386a144fd44db8f855d7e907256f8"
    with pytest.raises(ValueError):
        await coresys.host.logs.get_boot_id(3)


async def test_boot_ids_fallback(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting boot ids using fallback."""
    # Initial response has no log lines
    journald_gateway.content.feed_data(b"")
    journald_gateway.content.feed_eof()

    # Fallback contains exactly one with a boot ID
    boot_id_data = load_fixture("logs_boot_ids.txt")
    reader = asyncio.StreamReader(loop=asyncio.get_running_loop())
    reader.feed_data(boot_id_data.split("\n")[0].encode("utf-8"))
    reader.feed_eof()

    readers = [journald_gateway.content, reader]

    def get_side_effect(*args, **kwargs):
        journald_gateway.content = readers.pop(0)
        return journald_gateway.get.return_value

    journald_gateway.get.side_effect = get_side_effect

    assert await coresys.host.logs.get_boot_ids() == [
        "b2aca10d5ca54fb1b6fb35c85a0efca9"
    ]


async def test_identifiers(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting identifiers."""
    journald_gateway.content.feed_data(
        load_fixture("logs_identifiers.txt").encode("utf-8")
    )
    journald_gateway.content.feed_eof()

    # Mock is large so just look for a few different types of identifiers
    identifiers = await coresys.host.logs.get_identifiers()
    for identifier in [
        "addon_local_ssh",
        "hassio_dns",
        "hassio_supervisor",
        "kernel",
        "os-agent",
    ]:
        assert identifier in identifiers

    assert "" not in identifiers


async def test_connection_refused_handled(
    coresys: CoreSys, journald_gateway: MagicMock
):
    """Test connection refused is handled with HostServiceError."""
    with patch("supervisor.host.logs.ClientSession.get") as get:
        get.side_effect = UnixClientConnectorError(
            path="/run/systemd-journal-gatewayd.sock",
            connection_key=ConnectionKey(
                "localhost", None, False, False, None, None, None
            ),
            os_error=ConnectionRefusedError("Connection refused"),
        )

        with pytest.raises(HostServiceError):
            async with coresys.host.logs.journald_logs():
                pass
