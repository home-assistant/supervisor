"""Test UDisks2 Filesystem."""

from pathlib import Path

from dbus_fast import Variant
from dbus_fast.aio.message_bus import MessageBus
import pytest

from supervisor.dbus.udisks2.data import MountOptions, UnmountOptions
from supervisor.dbus.udisks2.filesystem import UDisks2Filesystem

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.udisks2_filesystem import Filesystem as FilesystemService


@pytest.fixture(name="filesystem_sda1_service")
async def fixture_filesystem_sda1_service(
    dbus_session_bus: MessageBus,
) -> FilesystemService:
    """Mock sda1 Filesystem service."""
    yield (
        await mock_dbus_services(
            {"udisks2_filesystem": "/org/freedesktop/UDisks2/block_devices/sda1"},
            dbus_session_bus,
        )
    )["udisks2_filesystem"]


@pytest.fixture(name="filesystem_sdb1_service")
async def fixture_filesystem_sdb1_service(
    dbus_session_bus: MessageBus,
) -> FilesystemService:
    """Mock sdb1 Filesystem service."""
    yield (
        await mock_dbus_services(
            {"udisks2_filesystem": "/org/freedesktop/UDisks2/block_devices/sdb1"},
            dbus_session_bus,
        )
    )["udisks2_filesystem"]


@pytest.fixture(name="sda1")
async def fixture_sda1(
    filesystem_sda1_service: FilesystemService, dbus_session_bus: MessageBus
) -> UDisks2Filesystem:
    """Return connected sda1 filesystem object."""
    filesystem = UDisks2Filesystem("/org/freedesktop/UDisks2/block_devices/sda1")
    await filesystem.connect(dbus_session_bus)
    return filesystem


async def test_filesystem_info(
    filesystem_sda1_service: FilesystemService,
    filesystem_sdb1_service: FilesystemService,
    dbus_session_bus: MessageBus,
):
    """Test filesystem info."""
    sda1 = UDisks2Filesystem("/org/freedesktop/UDisks2/block_devices/sda1")
    sdb1 = UDisks2Filesystem(
        "/org/freedesktop/UDisks2/block_devices/sdb1", sync_properties=False
    )

    assert sda1.size is None
    assert sda1.mount_points is None
    assert sdb1.size is None
    assert sdb1.mount_points is None

    await sda1.connect(dbus_session_bus)
    await sdb1.connect(dbus_session_bus)

    assert sda1.size == 250058113024
    assert sda1.mount_points == []
    assert sdb1.size == 67108864
    assert sdb1.mount_points == [Path("/mnt/data/supervisor/media/ext")]

    filesystem_sda1_service.emit_properties_changed({"MountPoints": [b"/mnt/media"]})
    await filesystem_sda1_service.ping()
    assert sda1.mount_points == [Path("/mnt/media")]

    filesystem_sda1_service.emit_properties_changed({}, ["MountPoints"])
    await filesystem_sda1_service.ping()
    await filesystem_sda1_service.ping()
    assert sda1.mount_points == []

    # Prop changes should not sync for this one
    filesystem_sdb1_service.emit_properties_changed({"MountPoints": [b"/mnt/media"]})
    await filesystem_sdb1_service.ping()
    assert sdb1.mount_points == [Path("/mnt/data/supervisor/media/ext")]


async def test_mount(
    sda1: UDisks2Filesystem, filesystem_sda1_service: FilesystemService
):
    """Test mount."""
    filesystem_sda1_service.Mount.calls.clear()
    assert await sda1.mount(MountOptions(fstype="gpt")) == "/run/media/dev/hassos_data"
    assert filesystem_sda1_service.Mount.calls == [
        (
            {
                "fstype": Variant("s", "gpt"),
                "auth.no_user_interaction": Variant("b", True),
            },
        )
    ]


async def test_unmount(
    sda1: UDisks2Filesystem, filesystem_sda1_service: FilesystemService
):
    """Test unmount."""
    filesystem_sda1_service.Unmount.calls.clear()
    await sda1.unmount(UnmountOptions(force=True))
    assert filesystem_sda1_service.Unmount.calls == [
        ({"force": Variant("b", True), "auth.no_user_interaction": Variant("b", True)},)
    ]


async def test_check(
    sda1: UDisks2Filesystem, filesystem_sda1_service: FilesystemService
):
    """Test check."""
    filesystem_sda1_service.Check.calls.clear()
    assert await sda1.check() is True
    assert filesystem_sda1_service.Check.calls == [
        ({"auth.no_user_interaction": Variant("b", True)},)
    ]


async def test_repair(
    sda1: UDisks2Filesystem, filesystem_sda1_service: FilesystemService
):
    """Test repair."""
    filesystem_sda1_service.Repair.calls.clear()
    assert await sda1.repair() is True
    assert filesystem_sda1_service.Repair.calls == [
        ({"auth.no_user_interaction": Variant("b", True)},)
    ]


async def test_set_label(
    sda1: UDisks2Filesystem, filesystem_sda1_service: FilesystemService
):
    """Test set label."""
    filesystem_sda1_service.SetLabel.calls.clear()
    await sda1.set_label("test")
    assert filesystem_sda1_service.SetLabel.calls == [
        (
            "/org/freedesktop/UDisks2/block_devices/sda1",
            "test",
            {"auth.no_user_interaction": Variant("b", True)},
        )
    ]
