"""Test OS API."""
from pathlib import Path, PosixPath

import pytest

from supervisor.coresys import CoreSys
from supervisor.exceptions import HassOSDataDiskError
from supervisor.hardware.data import Device

# pylint: disable=protected-access


@pytest.mark.asyncio
async def tests_datadisk_current(coresys: CoreSys):
    """Test current datadisk."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    assert coresys.os.datadisk.disk_used == PosixPath("/dev/sda")


@pytest.mark.asyncio
async def test_datadisk_move(coresys: CoreSys):
    """Test datadisk moved without exists device."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()
    coresys.os._available = True

    with pytest.raises(HassOSDataDiskError):
        await coresys.os.datadisk.migrate_disk(Path("/dev/sdaaaa"))


@pytest.mark.asyncio
async def test_datadisk_list(coresys: CoreSys):
    """Test docker info api."""
    await coresys.dbus.agent.connect()
    await coresys.dbus.agent.update()

    coresys.hardware.update_device(
        Device(
            "sda",
            Path("/dev/sda"),
            Path("/sys/bus/usb/000"),
            "block",
            None,
            [Path("/dev/serial/by-id/test")],
            {"ID_NAME": "xy", "MINOR": "0", "DEVTYPE": "disk"},
            [],
        )
    )
    coresys.hardware.update_device(
        Device(
            "sda1",
            Path("/dev/sda1"),
            Path("/sys/bus/usb/000/1"),
            "block",
            None,
            [Path("/dev/serial/by-id/test1")],
            {"ID_NAME": "xy", "MINOR": "1", "DEVTYPE": "partition"},
            [],
        )
    )

    assert coresys.os.datadisk.available_disks == [PosixPath("/dev/sda")]
