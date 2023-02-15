"""Test UDisks2 Filesystem."""

import asyncio
from pathlib import Path

from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.data import MountOptions, UnmountOptions
from supervisor.dbus.udisks2.filesystem import UDisks2Filesystem

from tests.common import fire_property_change_signal


@pytest.fixture(name="sda1")
async def fixture_sda1(dbus: list[str], dbus_bus: MessageBus) -> UDisks2Filesystem:
    """Return connected sda1 filesystem object."""
    filesystem = UDisks2Filesystem("/org/freedesktop/UDisks2/block_devices/sda1")
    await filesystem.connect(dbus_bus)
    return filesystem


async def test_filesystem_info(dbus: list[str], dbus_bus: MessageBus):
    """Test filesystem info."""
    sda1 = UDisks2Filesystem("/org/freedesktop/UDisks2/block_devices/sda1")
    sdb1 = UDisks2Filesystem(
        "/org/freedesktop/UDisks2/block_devices/sdb1", sync_properties=False
    )

    assert sda1.size is None
    assert sda1.mount_points is None
    assert sdb1.size is None
    assert sdb1.mount_points is None

    await sda1.connect(dbus_bus)
    await sdb1.connect(dbus_bus)

    assert sda1.size == 250058113024
    assert sda1.mount_points == []
    assert sdb1.size == 67108864
    assert sdb1.mount_points == [Path("/mnt/data/supervisor/media/ext")]

    fire_property_change_signal(
        sda1, {"MountPoints": [bytearray("/mnt/media", encoding="utf-8")]}
    )
    await asyncio.sleep(0)
    assert sda1.mount_points == [Path("/mnt/media")]

    with pytest.raises(AssertionError):
        fire_property_change_signal(
            sdb1, {"MountPoints": [bytearray("/mnt/media", encoding="utf-8")]}
        )


async def test_mount(dbus: list[str], sda1: UDisks2Filesystem):
    """Test mount."""
    assert await sda1.mount(MountOptions(fstype="gpt")) == "/run/media/dev/hassos_data"
    assert dbus == [
        "/org/freedesktop/UDisks2/block_devices/sda1-org.freedesktop.UDisks2.Filesystem.Mount"
    ]


async def test_unmount(dbus: list[str], sda1: UDisks2Filesystem):
    """Test unmount."""
    await sda1.unmount(UnmountOptions(force=True))
    assert dbus == [
        "/org/freedesktop/UDisks2/block_devices/sda1-org.freedesktop.UDisks2.Filesystem.Unmount"
    ]


async def test_check(dbus: list[str], sda1: UDisks2Filesystem):
    """Test check."""
    assert await sda1.check() is True
    assert dbus == [
        "/org/freedesktop/UDisks2/block_devices/sda1-org.freedesktop.UDisks2.Filesystem.Check"
    ]


async def test_repair(dbus: list[str], sda1: UDisks2Filesystem):
    """Test repair."""
    assert await sda1.repair() is True
    assert dbus == [
        "/org/freedesktop/UDisks2/block_devices/sda1-org.freedesktop.UDisks2.Filesystem.Repair"
    ]
