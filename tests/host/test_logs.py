"""Test host logs control."""

from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostNotSupportedError
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

    journald_gateway.feed_data(load_fixture("logs_export_host.txt").encode("utf-8"))
    journald_gateway.feed_eof()

    async with coresys.host.logs.journald_logs() as resp:
        line = await anext(
            journal_logs_reader(resp, log_formatter=LogFormatter.VERBOSE)
        )
        assert (
            line
            == "2024-03-04 03:52:56.193 homeassistant systemd[1]: Started Hostname Service."
        )

    with patch.object(
        LogsControl, "available", new=PropertyMock(return_value=False)
    ), pytest.raises(HostNotSupportedError):
        async with coresys.host.logs.journald_logs():
            pass


async def test_logs_coloured(coresys: CoreSys, journald_gateway: MagicMock):
    """Test ANSI control sequences being preserved in binary messages."""
    journald_gateway.feed_data(
        load_fixture("logs_export_supervisor.txt").encode("utf-8")
    )
    journald_gateway.feed_eof()

    async with coresys.host.logs.journald_logs() as resp:
        line = await anext(journal_logs_reader(resp))
        assert (
            line
            == "\x1b[32m24-03-04 23:56:56 INFO (MainThread) [__main__] Closing Supervisor\x1b[0m"
        )


async def test_boot_ids(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting boot ids."""
    journald_gateway.feed_data(load_fixture("logs_boot_ids.txt").encode("utf-8"))
    journald_gateway.feed_eof()

    assert await coresys.host.logs.get_boot_ids() == TEST_BOOT_IDS

    # Boot ID query should not be run again, mock a failure for it to ensure
    journald_gateway.side_effect = TimeoutError()
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


async def test_identifiers(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting identifiers."""
    journald_gateway.feed_data(load_fixture("logs_identifiers.txt").encode("utf-8"))
    journald_gateway.feed_eof()

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
