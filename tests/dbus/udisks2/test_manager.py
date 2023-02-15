"""Test UDisks2 Manager interface."""

import asyncio

from awesomeversion import AwesomeVersion
import pytest

from supervisor.coresys import CoreSys
from supervisor.dbus.udisks2.data import DeviceSpecification
from supervisor.exceptions import DBusNotConnectedError, DBusObjectError

from tests.common import fire_property_change_signal


async def test_udisks2_manager_info(coresys: CoreSys, dbus: list[str]):
    """Test udisks2 manager dbus connection."""
    dbus.clear()
    assert coresys.dbus.udisks2.supported_filesystems is None

    await coresys.dbus.udisks2.connect(coresys.dbus.bus)

    assert coresys.dbus.udisks2.supported_filesystems == [
        "ext4",
        "vfat",
        "ntfs",
        "exfat",
        "swap",
    ]
    assert coresys.dbus.udisks2.version == AwesomeVersion("2.9.2")
    assert {block.object_path for block in coresys.dbus.udisks2.block_devices} == {
        "/org/freedesktop/UDisks2/block_devices/loop0",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p1",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p2",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1p3",
        "/org/freedesktop/UDisks2/block_devices/sda",
        "/org/freedesktop/UDisks2/block_devices/sda1",
        "/org/freedesktop/UDisks2/block_devices/sdb",
        "/org/freedesktop/UDisks2/block_devices/sdb1",
        "/org/freedesktop/UDisks2/block_devices/zram1",
    }
    assert {drive.object_path for drive in coresys.dbus.udisks2.drives} == {
        "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
        "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
    }
    assert dbus == [
        "/org/freedesktop/UDisks2/Manager-org.freedesktop.UDisks2.Manager.GetBlockDevices"
    ]

    dbus.clear()
    fire_property_change_signal(
        coresys.dbus.udisks2, {"SupportedFilesystems": ["ext4"]}
    )
    await asyncio.sleep(0)
    assert coresys.dbus.udisks2.supported_filesystems == ["ext4"]
    assert dbus == []


async def test_get_block_device(coresys: CoreSys):
    """Test get block device by object path."""
    with pytest.raises(DBusNotConnectedError):
        coresys.dbus.udisks2.get_block_device(
            "/org/freedesktop/UDisks2/block_devices/sda1"
        )

    await coresys.dbus.udisks2.connect(coresys.dbus.bus)

    block_device = coresys.dbus.udisks2.get_block_device(
        "/org/freedesktop/UDisks2/block_devices/sda1"
    )
    assert block_device.id_label == "hassos-data"

    with pytest.raises(DBusObjectError):
        coresys.dbus.udisks2.get_block_device("non_existent")


async def test_get_drive(coresys: CoreSys):
    """Test get drive by object path."""
    with pytest.raises(DBusNotConnectedError):
        coresys.dbus.udisks2.get_drive(
            "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291"
        )

    await coresys.dbus.udisks2.connect(coresys.dbus.bus)

    drive = coresys.dbus.udisks2.get_drive(
        "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291"
    )
    assert drive.id == "BJTD4R-0x97cde291"

    with pytest.raises(DBusObjectError):
        coresys.dbus.udisks2.get_drive("non_existent")


async def test_resolve_device(coresys: CoreSys, dbus: list[str]):
    """Test resolve device."""
    with pytest.raises(DBusNotConnectedError):
        await coresys.dbus.udisks2.resolve_device(DeviceSpecification(path="/dev/sda1"))

    await coresys.dbus.udisks2.connect(coresys.dbus.bus)

    dbus.clear()
    devices = await coresys.dbus.udisks2.resolve_device(
        DeviceSpecification(path="/dev/sda1")
    )
    assert len(devices) == 1
    assert devices[0].id_label == "hassos-data"
    assert dbus == [
        "/org/freedesktop/UDisks2/Manager-org.freedesktop.UDisks2.Manager.ResolveDevice"
    ]
