"""Test UDisks2 Partition Table."""

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.const import PartitionTableType
from supervisor.dbus.udisks2.data import CreatePartitionOptions
from supervisor.dbus.udisks2.partition_table import UDisks2PartitionTable

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.udisks2_partition_table import (
    PartitionTable as PartitionTableService,
)


@pytest.fixture(name="partition_table_sda_service")
async def fixture_partition_table_sda_service(
    dbus_session_bus: MessageBus,
) -> PartitionTableService:
    """Mock sda Partition Table service."""
    yield (
        await mock_dbus_services(
            {"udisks2_partition_table": "/org/freedesktop/UDisks2/block_devices/sda"},
            dbus_session_bus,
        )
    )["udisks2_partition_table"]


@pytest.fixture(name="partition_table_sdb_service")
async def fixture_partition_table_sdb_service(
    dbus_session_bus: MessageBus,
) -> PartitionTableService:
    """Mock sdb Partition Table service."""
    yield (
        await mock_dbus_services(
            {"udisks2_partition_table": "/org/freedesktop/UDisks2/block_devices/sdb"},
            dbus_session_bus,
        )
    )["udisks2_partition_table"]


async def test_partition_table_info(
    partition_table_sda_service: PartitionTableService,
    partition_table_sdb_service: PartitionTableService,
    dbus_session_bus: MessageBus,
):
    """Test partition table info."""
    sda = UDisks2PartitionTable("/org/freedesktop/UDisks2/block_devices/sda")
    sdb = UDisks2PartitionTable(
        "/org/freedesktop/UDisks2/block_devices/sdb", sync_properties=False
    )

    assert sda.type is None
    assert sda.partitions is None
    assert sdb.type is None
    assert sdb.partitions is None

    await sda.connect(dbus_session_bus)
    await sdb.connect(dbus_session_bus)

    assert sda.type == PartitionTableType.GPT
    assert sda.partitions == ["/org/freedesktop/UDisks2/block_devices/sda1"]
    assert sdb.type == PartitionTableType.GPT
    assert sdb.partitions == ["/org/freedesktop/UDisks2/block_devices/sdb1"]

    partition_table_sda_service.emit_properties_changed(
        {
            "Partitions": [
                "/org/freedesktop/UDisks2/block_devices/sda1",
                "/org/freedesktop/UDisks2/block_devices/sda2",
            ]
        },
    )
    await partition_table_sda_service.ping()
    assert sda.partitions == [
        "/org/freedesktop/UDisks2/block_devices/sda1",
        "/org/freedesktop/UDisks2/block_devices/sda2",
    ]

    partition_table_sda_service.emit_properties_changed({}, ["Partitions"])
    await partition_table_sda_service.ping()
    await partition_table_sda_service.ping()
    assert sda.partitions == ["/org/freedesktop/UDisks2/block_devices/sda1"]

    # Prop changes should not sync for this one
    partition_table_sdb_service.emit_properties_changed(
        {
            "Partitions": [
                "/org/freedesktop/UDisks2/block_devices/sdb1",
                "/org/freedesktop/UDisks2/block_devices/sdb2",
            ]
        },
    )
    await partition_table_sdb_service.ping()
    assert sdb.partitions == ["/org/freedesktop/UDisks2/block_devices/sdb1"]


async def test_create_partition(
    partition_table_sda_service: PartitionTableService, dbus_session_bus: MessageBus
):
    """Test create partition."""
    sda = UDisks2PartitionTable("/org/freedesktop/UDisks2/block_devices/sda")
    await sda.connect(dbus_session_bus)

    assert (
        await sda.create_partition(
            offset=0,
            size=1000000,
            type_=PartitionTableType.DOS,
            name="hassos-data",
            options=CreatePartitionOptions(partition_type="primary"),
        )
        == "/org/freedesktop/UDisks2/block_devices/sda2"
    )
    assert partition_table_sda_service.CreatePartition.calls == [
        (
            0,
            1000000,
            "dos",
            "hassos-data",
            {
                "partition-type": Variant("s", "primary"),
                "auth.no_user_interaction": Variant("b", True),
            },
        )
    ]
