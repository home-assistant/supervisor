"""Test host logs control."""

from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HostNotSupportedError
from supervisor.host.logs import LogsControl

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

    async with coresys.host.logs.journald_logs() as resp:
        body = await resp.text()
        assert (
            "Oct 11 20:46:22 odroid-dev systemd[1]: Started Hostname Service." in body
        )

    with patch.object(
        LogsControl, "available", new=PropertyMock(return_value=False)
    ), pytest.raises(HostNotSupportedError):
        async with coresys.host.logs.journald_logs():
            pass


async def test_boot_ids(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting boot ids."""
    journald_gateway.return_value.__aenter__.return_value.text = AsyncMock(
        return_value=load_fixture("logs_boot_ids.txt")
    )

    assert TEST_BOOT_IDS == await coresys.host.logs.get_boot_ids()

    # Boot ID query should not be run again, mock a failure for it to ensure
    journald_gateway.side_effect = TimeoutError()
    assert TEST_BOOT_IDS == await coresys.host.logs.get_boot_ids()

    assert "b1c386a144fd44db8f855d7e907256f8" == await coresys.host.logs.get_boot_id(0)

    # -1 is previous boot. We have 2 boots so -2 is too far
    assert "b2aca10d5ca54fb1b6fb35c85a0efca9" == await coresys.host.logs.get_boot_id(-1)
    with pytest.raises(ValueError):
        await coresys.host.logs.get_boot_id(-2)

    # 1 is oldest boot and count up from there. We have 2 boots so 3 is too far
    assert "b2aca10d5ca54fb1b6fb35c85a0efca9" == await coresys.host.logs.get_boot_id(1)
    assert "b1c386a144fd44db8f855d7e907256f8" == await coresys.host.logs.get_boot_id(2)
    with pytest.raises(ValueError):
        await coresys.host.logs.get_boot_id(3)


async def test_identifiers(coresys: CoreSys, journald_gateway: MagicMock):
    """Test getting identifiers."""
    journald_gateway.return_value.__aenter__.return_value.text = AsyncMock(
        return_value=load_fixture("logs_identifiers.txt")
    )

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
