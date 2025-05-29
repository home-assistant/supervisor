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

TEST_BOOTS_IDS_NATIVE = [
    "77f66b1fd6b2416e8eebf509c9a470e6",
    "2411cf84b38a41939de746afc7a22e18",
    "3fa78d16a4ee4975b632d24dea52404c",
    "b81a432efb2d4a71a1e2d1b42892c187",
    "aeaa3d67efe9410ba7210cbee21bb022",
]


async def test_load(coresys: CoreSys):
    """Test load."""
    assert coresys.host.logs.default_identifiers == []

    await coresys.host.logs.load()
    assert coresys.host.logs.boot_ids == []

    # File is quite large so just check it loaded
    for identifier in ["kernel", "os-agent", "systemd"]:
        assert identifier in coresys.host.logs.default_identifiers


async def test_logs(journald_gateway: MagicMock, coresys: CoreSys):
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


async def test_logs_coloured(journald_gateway: MagicMock, coresys: CoreSys):
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


async def test_boot_ids(
    journald_gateway: MagicMock,
    coresys: CoreSys,
    without_journal_gatewayd_boots: MagicMock,
):
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


async def test_boot_ids_legacy_fallback(
    journald_gateway: MagicMock,
    coresys: CoreSys,
    without_journal_gatewayd_boots: MagicMock,
):
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


async def test_boot_ids_native(journald_gateway: MagicMock, coresys: CoreSys):
    """Test getting boot ids from /boots endpoint."""
    journald_gateway.content.feed_data(
        load_fixture("systemd_journal_boots.jsons").encode("utf-8")
    )
    journald_gateway.content.feed_eof()

    assert await coresys.host.logs.get_boot_ids() == TEST_BOOTS_IDS_NATIVE


async def test_identifiers(journald_gateway: MagicMock, coresys: CoreSys):
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
    journald_gateway: MagicMock, coresys: CoreSys
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


@pytest.mark.parametrize(
    "range_header,range_reparse",
    [
        ("entries=:-99:", "entries=:-99:18446744073709551615"),
        ("entries=:-99:100", "entries=:-99:100"),
        ("entries=cursor:0:100", "entries=cursor:0:100"),
    ],
)
async def test_range_header_reparse(
    journald_gateway: MagicMock, coresys: CoreSys, range_header: str, range_reparse: str
):
    """Test that range header with trailing colon contains num_entries."""
    async with coresys.host.logs.journald_logs(range_header=range_header):
        journald_gateway.get.assert_called_with(
            "/entries",
            headers={"Accept": "text/plain", "Range": range_reparse},
            params={},
            timeout=None,
        )
