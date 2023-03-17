"""Test UDisks2 Manager interface."""

from awesomeversion import AwesomeVersion
from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2 import UDisks2
from supervisor.dbus.udisks2.data import DeviceSpecification
from supervisor.exceptions import DBusNotConnectedError, DBusObjectError

from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)


@pytest.fixture(name="udisks2_manager_service", autouse=True)
async def fixture_udisks2_manager_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]]
) -> UDisks2ManagerService:
    """Mock UDisks2 Manager service."""
    yield udisks2_services["udisks2_manager"]


async def test_udisks2_manager_info(
    udisks2_manager_service: UDisks2ManagerService, dbus_session_bus: MessageBus
):
    """Test udisks2 manager dbus connection."""
    udisks2_manager_service.GetBlockDevices.calls.clear()
    udisks2 = UDisks2()

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


async def test_get_block_device(dbus_session_bus: MessageBus):
    """Test get block device by object path."""
    udisks2 = UDisks2()

    with pytest.raises(DBusNotConnectedError):
        udisks2.get_block_device("/org/freedesktop/UDisks2/block_devices/sda1")

    await udisks2.connect(dbus_session_bus)

    block_device = udisks2.get_block_device(
        "/org/freedesktop/UDisks2/block_devices/sda1"
    )
    assert block_device.id_label == "hassos-data"

    with pytest.raises(DBusObjectError):
        udisks2.get_block_device("non_existent")


async def test_get_drive(dbus_session_bus: MessageBus):
    """Test get drive by object path."""
    udisks2 = UDisks2()

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
    udisks2 = UDisks2()

    with pytest.raises(DBusNotConnectedError):
        await udisks2.resolve_device(DeviceSpecification(path="/dev/sda1"))

    await udisks2.connect(dbus_session_bus)

    devices = await udisks2.resolve_device(DeviceSpecification(path="/dev/sda1"))
    assert len(devices) == 1
    assert devices[0].id_label == "hassos-data"
    assert udisks2_manager_service.ResolveDevice.calls == [
        (
            {"path": Variant("s", "/dev/sda1")},
            {"auth.no_user_interaction": Variant("b", True)},
        )
    ]
