"""Test UDisks2 Manager interface."""

import asyncio
from pathlib import Path

from awesomeversion import AwesomeVersion
from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2 import UDisks2Manager
from supervisor.dbus.udisks2.const import PartitionTableType
from supervisor.dbus.udisks2.data import DeviceSpecification
from supervisor.exceptions import DBusNotConnectedError, DBusObjectError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.udisks2 import UDisks2 as UDisks2Service
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)


@pytest.fixture(name="udisks2_manager_service")
async def fixture_udisks2_manager_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> UDisks2ManagerService:
    """Mock UDisks2 Manager service."""
    yield udisks2_services["udisks2_manager"]


@pytest.fixture(name="udisks2_service")
async def fixture_udisks2_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> UDisks2Service:
    """Mock UDisks2 base service."""
    yield udisks2_services["udisks2"]


async def test_udisks2_manager_info(
    udisks2_manager_service: UDisks2ManagerService, dbus_session_bus: MessageBus
):
    """Test udisks2 manager dbus connection."""
    udisks2_manager_service.GetBlockDevices.calls.clear()
    udisks2 = UDisks2Manager()

    assert udisks2.supported_filesystems is None

    await udisks2.connect(dbus_session_bus)

    assert udisks2.supported_filesystems == [
        "ext4",
        "vfat",
        "ntfs",
        "exfat",
        "swap",
    ]
    assert udisks2.version == AwesomeVersion("2.9.2")
    assert {block.object_path for block in udisks2.block_devices} == {
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
    assert {drive.object_path for drive in udisks2.drives} == {
        "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
        "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
        "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
    }
    assert udisks2_manager_service.GetBlockDevices.calls == [
        ({"auth.no_user_interaction": Variant("b", True)},)
    ]

    udisks2_manager_service.GetBlockDevices.calls.clear()
    udisks2_manager_service.emit_properties_changed({"SupportedFilesystems": ["ext4"]})
    await udisks2_manager_service.ping()
    assert udisks2.supported_filesystems == ["ext4"]
    assert udisks2_manager_service.GetBlockDevices.calls == []

    udisks2_manager_service.emit_properties_changed({}, ["SupportedFilesystems"])
    await udisks2_manager_service.ping()
    await udisks2_manager_service.ping()
    await (
        udisks2_manager_service.ping()
    )  # Three pings: signal, get all properties and get block devices
    assert udisks2.supported_filesystems == [
        "ext4",
        "vfat",
        "ntfs",
        "exfat",
        "swap",
    ]
    assert udisks2_manager_service.GetBlockDevices.calls == [
        ({"auth.no_user_interaction": Variant("b", True)},)
    ]


async def test_update_checks_devices_and_drives(dbus_session_bus: MessageBus):
    """Test update rechecks block devices and drives correctly."""
    mocked = await mock_dbus_services(
        {
            "udisks2": None,
            "udisks2_manager": None,
            "udisks2_block": [
                "/org/freedesktop/UDisks2/block_devices/sda",
                "/org/freedesktop/UDisks2/block_devices/sda1",
                "/org/freedesktop/UDisks2/block_devices/sdb",
            ],
            "udisks2_drive": [
                "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56",
                "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6",
            ],
        },
        dbus_session_bus,
    )
    udisks2_manager_service: UDisks2ManagerService = mocked["udisks2_manager"]
    udisks2_manager_service.block_devices = [
        "/org/freedesktop/UDisks2/block_devices/sda",
        "/org/freedesktop/UDisks2/block_devices/sda1",
        "/org/freedesktop/UDisks2/block_devices/sdb",
    ]

    udisks2 = UDisks2Manager()
    await udisks2.connect(dbus_session_bus)

    assert len(udisks2.block_devices) == 3
    assert (
        udisks2.get_block_device(
            "/org/freedesktop/UDisks2/block_devices/sda"
        ).partition_table
        is None
    )
    assert (
        udisks2.get_block_device(
            "/org/freedesktop/UDisks2/block_devices/sda1"
        ).filesystem
        is None
    )
    sdb = udisks2.get_block_device("/org/freedesktop/UDisks2/block_devices/sdb")
    assert sdb.is_connected is True
    with pytest.raises(DBusObjectError):
        udisks2.get_block_device("/org/freedesktop/UDisks2/block_devices/mmcblk1")

    assert len(udisks2.drives) == 2
    assert (
        udisks2.get_drive(
            "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56"
        ).is_connected
        is True
    )
    flash_disk = udisks2.get_drive(
        "/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6"
    )
    assert flash_disk.is_connected is True
    with pytest.raises(DBusObjectError):
        udisks2.get_drive("/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291")

    await mock_dbus_services(
        {
            "udisks2_block": "/org/freedesktop/UDisks2/block_devices/mmcblk1",
            "udisks2_drive": "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291",
            "udisks2_filesystem": "/org/freedesktop/UDisks2/block_devices/sda1",
            "udisks2_partition_table": "/org/freedesktop/UDisks2/block_devices/sda",
        },
        dbus_session_bus,
    )
    udisks2_manager_service.block_devices = [
        "/org/freedesktop/UDisks2/block_devices/sda",
        "/org/freedesktop/UDisks2/block_devices/sda1",
        "/org/freedesktop/UDisks2/block_devices/mmcblk1",
    ]

    await udisks2.update()

    assert len(udisks2.block_devices) == 3
    assert (
        udisks2.get_block_device(
            "/org/freedesktop/UDisks2/block_devices/sda"
        ).partition_table.type
        == PartitionTableType.GPT
    )
    assert (
        udisks2.get_block_device(
            "/org/freedesktop/UDisks2/block_devices/sda1"
        ).filesystem.mount_points
        == []
    )
    assert (
        udisks2.get_block_device(
            "/org/freedesktop/UDisks2/block_devices/mmcblk1"
        ).is_connected
        is True
    )
    with pytest.raises(DBusObjectError):
        udisks2.get_block_device("/org/freedesktop/UDisks2/block_devices/sdb")
    assert sdb.is_connected is False
    assert sdb.is_shutdown is True

    assert len(udisks2.drives) == 2
    assert (
        udisks2.get_drive(
            "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56"
        ).is_connected
        is True
    )
    assert (
        udisks2.get_drive(
            "/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291"
        ).is_connected
        is True
    )
    with pytest.raises(DBusObjectError):
        udisks2.get_drive("/org/freedesktop/UDisks2/drives/Generic_Flash_Disk_61BCDDB6")
    assert flash_disk.is_connected is False
    assert flash_disk.is_shutdown is True


async def test_get_block_device(
    udisks2_manager_service: UDisks2ManagerService, dbus_session_bus: MessageBus
):
    """Test get block device by object path."""
    udisks2 = UDisks2Manager()

    with pytest.raises(DBusNotConnectedError):
        udisks2.get_block_device("/org/freedesktop/UDisks2/block_devices/sda1")

    await udisks2.connect(dbus_session_bus)

    block_device = udisks2.get_block_device(
        "/org/freedesktop/UDisks2/block_devices/sda1"
    )
    assert block_device.id_label == "hassos-data-old"

    with pytest.raises(DBusObjectError):
        udisks2.get_block_device("non_existent")


async def test_get_drive(
    udisks2_manager_service: UDisks2ManagerService, dbus_session_bus: MessageBus
):
    """Test get drive by object path."""
    udisks2 = UDisks2Manager()

    with pytest.raises(DBusNotConnectedError):
        udisks2.get_drive("/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291")

    await udisks2.connect(dbus_session_bus)

    drive = udisks2.get_drive("/org/freedesktop/UDisks2/drives/BJTD4R_0x97cde291")
    assert drive.id == "BJTD4R-0x97cde291"

    with pytest.raises(DBusObjectError):
        udisks2.get_drive("non_existent")


async def test_resolve_device(
    udisks2_manager_service: UDisks2ManagerService, dbus_session_bus: MessageBus
):
    """Test resolve device."""
    udisks2_manager_service.ResolveDevice.calls.clear()
    udisks2 = UDisks2Manager()

    with pytest.raises(DBusNotConnectedError):
        await udisks2.resolve_device(DeviceSpecification(path=Path("/dev/sda1")))

    await udisks2.connect(dbus_session_bus)

    devices = await udisks2.resolve_device(DeviceSpecification(path=Path("/dev/sda1")))
    assert len(devices) == 1
    assert devices[0].id_label == "hassos-data-old"
    assert udisks2_manager_service.ResolveDevice.calls == [
        (
            {"path": Variant("s", "/dev/sda1")},
            {"auth.no_user_interaction": Variant("b", True)},
        )
    ]


async def test_block_devices_add_remove_signals(
    udisks2_service: UDisks2Service, dbus_session_bus: MessageBus
):
    """Test signals processed for added and removed block devices."""
    udisks2 = UDisks2Manager()
    await udisks2.connect(dbus_session_bus)

    assert any(
        device
        for device in udisks2.block_devices
        if device.object_path == "/org/freedesktop/UDisks2/block_devices/zram1"
    )
    udisks2_service.InterfacesRemoved(
        "/org/freedesktop/UDisks2/block_devices/zram1",
        ["org.freedesktop.UDisks2.Block"],
    )
    await udisks2_service.ping()

    assert not any(
        device
        for device in udisks2.block_devices
        if device.object_path == "/org/freedesktop/UDisks2/block_devices/zram1"
    )

    udisks2_service.InterfacesAdded(
        "/org/freedesktop/UDisks2/block_devices/zram1",
        {
            "org.freedesktop.UDisks2.Block": {
                "Device": Variant("ay", b"/dev/zram1"),
                "PreferredDevice": Variant("ay", b"/dev/zram1"),
                "DeviceNumber": Variant("t", 64769),
                "Id": Variant("s", ""),
                "IdUsage": Variant("s", ""),
                "IdType": Variant("s", ""),
                "IdVersion": Variant("s", ""),
                "IdLabel": Variant("s", ""),
                "IdUUID": Variant("s", ""),
            }
        },
    )
    await udisks2_service.ping()
    await asyncio.sleep(0.1)
    assert any(
        device
        for device in udisks2.block_devices
        if device.object_path == "/org/freedesktop/UDisks2/block_devices/zram1"
    )
