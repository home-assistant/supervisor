"""Test UDisks2 Block Device interface."""

import asyncio
from pathlib import Path

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.block import UDisks2Block
from supervisor.dbus.udisks2.const import FormatType, PartitionTableType
from supervisor.dbus.udisks2.data import FormatOptions

from tests.common import fire_property_change_signal


async def test_block_device_info(dbus: list[str], dbus_bus: MessageBus):
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

    await sda.connect(dbus_bus)
    await sda1.connect(dbus_bus)

    assert sda.drive == "/org/freedesktop/UDisks2/drives/SSK_SSK_Storage_DF56419883D56"
    assert sda.device == Path("/dev/sda")
    assert sda.id_label == ""
    assert sda.partition_table.type == PartitionTableType.GPT
    assert sda.filesystem is None

    assert sda1.id_label == "hassos-data"
    assert sda1.symlinks == [
        Path("/dev/disk/by-id/usb-SSK_SSK_Storage_DF56419883D56-0:0-part1"),
        Path("/dev/disk/by-label/hassos-data"),
        Path("/dev/disk/by-partlabel/hassos-data-external"),
        Path("/dev/disk/by-partuuid/6f3f99f4-4d34-476b-b051-77886da57fa9"),
        Path(
            "/dev/disk/by-path/platform-xhci-hcd.1.auto-usb-0:1.4:1.0-scsi-0:0:0:0-part1"
        ),
        Path("/dev/disk/by-uuid/b82b23cb-0c47-4bbb-acf5-2a2afa8894a2"),
    ]
    assert sda1.partition_table is None
    assert sda1.filesystem.mount_points == []

    fire_property_change_signal(sda, {"IdLabel": "test"})
    await asyncio.sleep(0)
    assert sda.id_label == "test"

    with pytest.raises(AssertionError):
        fire_property_change_signal(sda1)


async def test_format(dbus: list[str], dbus_bus: MessageBus):
    """Test formatting block device."""
    sda = UDisks2Block("/org/freedesktop/UDisks2/block_devices/sda")
    await sda.connect(dbus_bus)

    await sda.format(FormatType.GPT, FormatOptions(label="test"))
    assert dbus == [
        "/org/freedesktop/UDisks2/block_devices/sda-org.freedesktop.UDisks2.Block.Format"
    ]
