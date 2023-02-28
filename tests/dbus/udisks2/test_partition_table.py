"""Test UDisks2 Partition Table."""

import asyncio

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.const import PartitionTableType
from supervisor.dbus.udisks2.data import CreatePartitionOptions
from supervisor.dbus.udisks2.partition_table import UDisks2PartitionTable

from tests.common import fire_property_change_signal


async def test_partition_table_info(dbus: list[str], dbus_bus: MessageBus):
    """Test partition table info."""
    sda = UDisks2PartitionTable("/org/freedesktop/UDisks2/block_devices/sda")
    sdb = UDisks2PartitionTable(
        "/org/freedesktop/UDisks2/block_devices/sdb", sync_properties=False
    )

    assert sda.type is None
    assert sda.partitions is None
    assert sdb.type is None
    assert sdb.partitions is None

    await sda.connect(dbus_bus)
    await sdb.connect(dbus_bus)

    assert sda.type == PartitionTableType.GPT
    assert sda.partitions == ["/org/freedesktop/UDisks2/block_devices/sda1"]
    assert sdb.type == PartitionTableType.GPT
    assert sdb.partitions == ["/org/freedesktop/UDisks2/block_devices/sdb1"]

    fire_property_change_signal(
        sda,
        {
            "Partitions": [
                "/org/freedesktop/UDisks2/block_devices/sda1",
                "/org/freedesktop/UDisks2/block_devices/sda2",
            ]
        },
    )
    await asyncio.sleep(0)
    assert sda.partitions == [
        "/org/freedesktop/UDisks2/block_devices/sda1",
        "/org/freedesktop/UDisks2/block_devices/sda2",
    ]

    with pytest.raises(AssertionError):
        fire_property_change_signal(
            sdb,
            {
                "MountPoints": [
                    "/org/freedesktop/UDisks2/block_devices/sdb",
                    "/org/freedesktop/UDisks2/block_devices/sdb",
                ]
            },
        )


async def test_create_partition(dbus: list[str], dbus_bus: MessageBus):
    """Test create partition."""
    sda = UDisks2PartitionTable("/org/freedesktop/UDisks2/block_devices/sda")
    await sda.connect(dbus_bus)

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
    assert dbus == [
        "/org/freedesktop/UDisks2/block_devices/sda-org.freedesktop.UDisks2.PartitionTable.CreatePartition"
    ]
