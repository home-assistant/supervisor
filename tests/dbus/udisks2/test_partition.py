"""Test UDisks2 Partition."""

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.data import DeletePartitionOptions
from supervisor.dbus.udisks2.partition import UDisks2Partition
from supervisor.exceptions import DBusNotConnectedError

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.udisks2_partition import Partition as PartitionService


@pytest.fixture(name="partition_sda1_service")
async def fixture_partition_sda1_service(
    dbus_session_bus: MessageBus,
) -> PartitionService:
    """Mock sda1 Partition service."""
    yield (
        await mock_dbus_services(
            {"udisks2_partition": "/org/freedesktop/UDisks2/block_devices/sda1"},
            dbus_session_bus,
        )
    )["udisks2_partition"]


@pytest.fixture(name="partition_sdb1_service")
async def fixture_partition_sdb_service(
    dbus_session_bus: MessageBus,
) -> PartitionService:
    """Mock sdb1 Partition service."""
    yield (
        await mock_dbus_services(
            {"udisks2_partition": "/org/freedesktop/UDisks2/block_devices/sdb1"},
            dbus_session_bus,
        )
    )["udisks2_partition"]


async def test_partition_table_info(
    partition_sda1_service: PartitionService,
    partition_sdb1_service: PartitionService,
    dbus_session_bus: MessageBus,
):
    """Test partition table info."""
    sda1 = UDisks2Partition("/org/freedesktop/UDisks2/block_devices/sda1")
    sdb1 = UDisks2Partition(
        "/org/freedesktop/UDisks2/block_devices/sdb1", sync_properties=False
    )

    assert sda1.name_ is None
    assert sda1.size is None
    assert sdb1.name_ is None
    assert sdb1.size is None

    await sda1.connect(dbus_session_bus)
    await sdb1.connect(dbus_session_bus)

    assert sda1.name_ == "hassos-data-external"
    assert sda1.size == 250058113024
    assert sdb1.name_ == ""
    assert sdb1.size == 67108864

    partition_sda1_service.emit_properties_changed({"Name": "test"})
    await partition_sda1_service.ping()
    assert sda1.name_ == "test"

    partition_sda1_service.emit_properties_changed({}, ["Name"])
    await partition_sda1_service.ping()
    await partition_sda1_service.ping()
    assert sda1.name_ == "hassos-data-external"

    # Prop changes should not sync for this one
    partition_sdb1_service.emit_properties_changed({"Name": "test"})
    await partition_sdb1_service.ping()
    assert sdb1.name_ == ""


async def test_set_type(
    partition_sda1_service: PartitionService, dbus_session_bus: MessageBus
):
    """Test setting partition type."""
    partition_sda1_service.SetType.calls.clear()
    sda1 = UDisks2Partition("/org/freedesktop/UDisks2/block_devices/sda1")

    with pytest.raises(DBusNotConnectedError):
        await sda1.set_type("0FC63DAF-8483-4772-8E79-3D69D8477DE4")

    await sda1.connect(dbus_session_bus)

    await sda1.set_type("0FC63DAF-8483-4772-8E79-3D69D8477DE4")

    assert partition_sda1_service.SetType.calls == [
        (
            "0FC63DAF-8483-4772-8E79-3D69D8477DE4",
            {"auth.no_user_interaction": Variant("b", True)},
        )
    ]


async def test_set_name(
    partition_sda1_service: PartitionService, dbus_session_bus: MessageBus
):
    """Test setting partition name."""
    partition_sda1_service.SetName.calls.clear()
    sda1 = UDisks2Partition("/org/freedesktop/UDisks2/block_devices/sda1")

    with pytest.raises(DBusNotConnectedError):
        await sda1.set_name("test")

    await sda1.connect(dbus_session_bus)

    await sda1.set_name("test")

    assert partition_sda1_service.SetName.calls == [
        ("test", {"auth.no_user_interaction": Variant("b", True)})
    ]


async def test_resize(
    partition_sda1_service: PartitionService, dbus_session_bus: MessageBus
):
    """Test resizing partition."""
    partition_sda1_service.Resize.calls.clear()
    sda1 = UDisks2Partition("/org/freedesktop/UDisks2/block_devices/sda1")

    with pytest.raises(DBusNotConnectedError):
        await sda1.resize()

    await sda1.connect(dbus_session_bus)

    await sda1.resize()

    assert partition_sda1_service.Resize.calls == [
        (0, {"auth.no_user_interaction": Variant("b", True)})
    ]


async def test_delete(
    partition_sda1_service: PartitionService, dbus_session_bus: MessageBus
):
    """Test deleting partition."""
    partition_sda1_service.Delete.calls.clear()
    sda1 = UDisks2Partition("/org/freedesktop/UDisks2/block_devices/sda1")

    with pytest.raises(DBusNotConnectedError):
        await sda1.delete(DeletePartitionOptions(tear_down=True))

    await sda1.connect(dbus_session_bus)

    await sda1.delete(DeletePartitionOptions(tear_down=True))

    assert partition_sda1_service.Delete.calls == [
        (
            {
                "tear-down": Variant("b", True),
                "auth.no_user_interaction": Variant("b", True),
            },
        )
    ]
