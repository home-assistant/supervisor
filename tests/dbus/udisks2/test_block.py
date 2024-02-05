"""Test UDisks2 Block Device interface."""

from pathlib import Path
from unittest.mock import patch

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.block import UDisks2Block
from supervisor.dbus.udisks2.const import FormatType, PartitionTableType
from supervisor.dbus.udisks2.data import FormatOptions
from supervisor.dbus.udisks2.filesystem import UDisks2Filesystem
from supervisor.dbus.udisks2.partition import UDisks2Partition
from supervisor.dbus.udisks2.partition_table import UDisks2PartitionTable
from supervisor.utils.dbus import DBus

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.udisks2_block import Block as BlockService


@pytest.fixture(name="block_sda_service")
async def fixture_block_sda_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> BlockService:
    """Mock sda Block service."""
    yield udisks2_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sda"
    ]


@pytest.fixture(name="block_sda1_service")
async def fixture_block_sda1_service(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
) -> BlockService:
    """Mock sda1 Block service."""
    yield udisks2_services["udisks2_block"][
        "/org/freedesktop/UDisks2/block_devices/sda1"
    ]


async def test_block_device_info(
    block_sda_service: BlockService,
    block_sda1_service: BlockService,
    dbus_session_bus: MessageBus,
):
    """Test block device info."""
    sda = UDisks2Block("/org/freedesktop/UDisks2/block_devices/sda")
    sda1 = UDisks2Block(
        "/org/freedesktop/UDisks2/block_devices/sda1", sync_properties=False
    )

    assert sda.drive is None
    assert sda.device is None
    assert sda.id_label is None
    assert sda.partition_table is None
    assert sda1.id_label is None
    assert sda1.symlinks is None
    assert sda1.filesystem is None
    assert sda1.partition is None

    await sda.connect(dbus_session_bus)
    await sda1.connect(dbus_session_bus)

    assert sda.drive == "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56"
    assert sda.device == Path("/dev/sda")
    assert sda.id_label == ""
    assert sda.partition_table.type == PartitionTableType.GPT
    assert sda.filesystem is None
    assert sda.partition is None

    assert sda1.id_label == "hassos-data-old"
    assert sda1.symlinks == [
        Path("/dev/disk/by-id/usb-SSK_SSK_Storage_DF56419883D56-0:0-part1"),
        Path("/dev/disk/by-label/hassos-data-old"),
        Path("/dev/disk/by-partlabel/hassos-data-external"),
        Path("/dev/disk/by-partuuid/6f3f99f4-4d34-476b-b051-77886da57fa9"),
        Path(
            "/dev/disk/by-path/platform-xhci-hcd.1.auto-usb-0:1.4:1.0-scsi-0:0:0:0-part1"
        ),
        Path("/dev/disk/by-uuid/b82b23cb-0c47-4bbb-acf5-2a2afa8894a2"),
    ]
    assert sda1.partition_table is None
    assert sda1.filesystem.mount_points == []
    assert sda1.partition.number == 1

    block_sda_service.emit_properties_changed({"IdLabel": "test"})
    await block_sda_service.ping()
    assert sda.id_label == "test"

    block_sda_service.emit_properties_changed({}, ["IdLabel"])
    await block_sda_service.ping()
    await block_sda_service.ping()
    assert sda.id_label == ""

    # Prop changes should not sync for this one
    block_sda1_service.emit_properties_changed({"IdLabel": "test"})
    await block_sda1_service.ping()
    assert sda1.id_label == "hassos-data-old"


async def test_format(block_sda_service: BlockService, dbus_session_bus: MessageBus):
    """Test formatting block device."""
    block_sda_service.Format.calls.clear()
    sda = UDisks2Block("/org/freedesktop/UDisks2/block_devices/sda")
    await sda.connect(dbus_session_bus)

    await sda.format(FormatType.GPT, FormatOptions(label="test"))
    assert block_sda_service.Format.calls == [
        (
            "gpt",
            {
                "label": Variant("s", "test"),
                "auth.no_user_interaction": Variant("b", True),
            },
        )
    ]


async def test_check_type(dbus_session_bus: MessageBus):
    """Test block device changes types correctly."""
    block_services = (
        await mock_dbus_services(
            {
                "udisks2_block": [
                    "/org/freedesktop/UDisks2/block_devices/sda",
                    "/org/freedesktop/UDisks2/block_devices/sda1",
                ]
            },
            dbus_session_bus,
        )
    )["udisks2_block"]
    sda_block_service = block_services["/org/freedesktop/UDisks2/block_devices/sda"]
    sda1_block_service = block_services["/org/freedesktop/UDisks2/block_devices/sda1"]

    sda = UDisks2Block("/org/freedesktop/UDisks2/block_devices/sda")
    sda1 = UDisks2Block("/org/freedesktop/UDisks2/block_devices/sda1")
    await sda.connect(dbus_session_bus)
    await sda1.connect(dbus_session_bus)

    # Connected but neither are filesystems, partitions or partition tables
    assert sda.partition_table is None
    assert sda1.filesystem is None
    assert sda1.partition is None
    assert sda.id_label == ""
    assert sda1.id_label == "hassos-data-old"

    # Store current introspection then make sda into a partition table and sda1 into a filesystem
    orig_introspection = await sda.dbus.introspect()
    services = await mock_dbus_services(
        {
            "udisks2_partition_table": "/org/freedesktop/UDisks2/block_devices/sda",
            "udisks2_filesystem": "/org/freedesktop/UDisks2/block_devices/sda1",
            "udisks2_partition": "/org/freedesktop/UDisks2/block_devices/sda1",
        },
        dbus_session_bus,
    )
    sda_pt_service = services["udisks2_partition_table"]
    sda1_fs_service = services["udisks2_filesystem"]
    sda1_part_service = services["udisks2_partition"]

    await sda.check_type()
    await sda1.check_type()

    # Check that the type is now correct and property changes are syncing
    assert sda.partition_table
    assert sda1.filesystem
    assert sda1.partition

    partition_table: UDisks2PartitionTable = sda.partition_table
    filesystem: UDisks2Filesystem = sda1.filesystem
    partition: UDisks2Partition = sda1.partition
    assert partition_table.type == PartitionTableType.GPT
    assert filesystem.size == 250058113024
    assert partition.name_ == "hassos-data-external"

    sda_pt_service.emit_properties_changed({"Type": "dos"})
    await sda_pt_service.ping()
    assert partition_table.type == PartitionTableType.DOS

    sda1_fs_service.emit_properties_changed({"Size": 100})
    await sda1_fs_service.ping()
    assert filesystem.size == 100

    sda1_part_service.emit_properties_changed({"Name": "test"})
    await sda1_part_service.ping()
    assert partition.name_ == "test"

    # Force introspection to return the original block device only introspection and re-check type
    with patch.object(DBus, "introspect", return_value=orig_introspection):
        await sda.check_type()
        await sda1.check_type()

    # Check that it's a connected block device and no longer the other types
    assert sda.is_connected is True
    assert sda1.is_connected is True
    assert sda.partition_table is None
    assert sda1.filesystem is None
    assert sda1.partition is None

    # Property changes should still sync for the block devices
    sda_block_service.emit_properties_changed({"IdLabel": "test"})
    await sda_block_service.ping()
    assert sda.id_label == "test"

    sda1_block_service.emit_properties_changed({"IdLabel": "test"})
    await sda1_block_service.ping()
    assert sda1.id_label == "test"

    # Property changes should stop syncing for the now unused dbus objects
    sda_pt_service.emit_properties_changed({"Type": "gpt"})
    await sda_pt_service.ping()
    assert partition_table.type == PartitionTableType.DOS

    sda1_fs_service.emit_properties_changed({"Size": 250058113024})
    await sda1_fs_service.ping()
    assert filesystem.size == 100

    sda1_part_service.emit_properties_changed({"Name": "hassos-data-external"})
    await sda1_part_service.ping()
    assert partition.name_ == "test"
