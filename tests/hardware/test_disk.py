"""Test hardware utils."""

# pylint: disable=protected-access
import errno
import os
from pathlib import Path
from unittest.mock import patch

from dbus_fast.aio import MessageBus
import pytest

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device
from supervisor.resolution.const import UnhealthyReason

from tests.common import mock_dbus_services
from tests.dbus_service_mocks.base import DBusServiceMock
from tests.dbus_service_mocks.udisks2_manager import (
    UDisks2Manager as UDisks2ManagerService,
)
from tests.dbus_service_mocks.udisks2_nvme_controller import (
    NVMeController as NVMeControllerService,
)

MOCK_MOUNTINFO = """790 750 259:8 /supervisor /data rw,relatime master:118 - ext4 /dev/nvme0n1p8 rw,commit=30
810 750 0:24 /systemd-journal-gatewayd.sock /run/systemd-journal-gatewayd.sock rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
811 750 0:24 /supervisor /run/os rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
813 750 0:24 /udev /run/udev ro,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
814 750 0:24 /machine-id /etc/machine-id ro - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
815 750 0:24 /docker.sock /run/docker.sock rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
816 750 0:24 /dbus /run/dbus ro,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
820 750 0:24 /containerd/containerd.sock /run/containerd/containerd.sock rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
821 750 0:24 /systemd/journal/socket /run/systemd/journal/socket rw,nosuid,nodev - tmpfs tmpfs rw,size=405464k,nr_inodes=819200,mode=755
"""


@pytest.fixture(name="nvme_data_disk")
async def fixture_nvme_data_disk(
    udisks2_services: dict[str, DBusServiceMock | dict[str, DBusServiceMock]],
    coresys: CoreSys,
    dbus_session_bus: MessageBus,
) -> NVMeControllerService:
    """Mock using an NVMe data disk."""
    nvme_service = (
        await mock_dbus_services(
            {
                "udisks2_block": "/org/freedesktop/UDisks2/block_devices/nvme0n1",
                "udisks2_drive": "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC",
                "udisks2_nvme_controller": "/org/freedesktop/UDisks2/drives/Samsung_SSD_970_EVO_Plus_2TB_S40123456789ABC",
            },
            dbus_session_bus,
        )
    )["udisks2_nvme_controller"]
    udisks2_manager: UDisks2ManagerService = udisks2_services["udisks2_manager"]
    udisks2_manager.block_devices.append(
        "/org/freedesktop/UDisks2/block_devices/nvme0n1"
    )
    await coresys.dbus.udisks2.update()

    with (
        patch(
            "supervisor.hardware.disk.Path.read_text",
            return_value=MOCK_MOUNTINFO,
        ),
        patch("supervisor.hardware.disk.Path.is_block_device", return_value=True),
        patch(
            "supervisor.hardware.disk.Path.resolve",
            return_value=Path(
                "/sys/devices/platform/soc/ffe07000.nvme/nvme_host/nvme0/nvme0:0000/block/nvme0n1/nvme0n1p8"
            ),
        ),
    ):
        yield nvme_service


def test_system_partition_disk(coresys: CoreSys):
    """Test if it is a system disk/partition."""
    disk = Device(
        "sda1",
        Path("/dev/sda1"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10"},
        [],
    )

    assert not coresys.hardware.disk.is_used_by_system(disk)

    disk = Device(
        "sda1",
        Path("/dev/sda1"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10", "ID_FS_LABEL": "hassos-overlay"},
        [],
    )

    assert coresys.hardware.disk.is_used_by_system(disk)

    coresys.hardware.update_device(disk)
    disk_root = Device(
        "sda",
        Path("/dev/sda"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "0"},
        [Path("/dev/sda1")],
    )

    assert coresys.hardware.disk.is_used_by_system(disk_root)


def test_free_space(coresys):
    """Test free space helper."""
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0**3))):
        free = coresys.hardware.disk.get_disk_free_space("/data")

    assert free == 2.0


def test_total_space(coresys):
    """Test total space helper."""
    with patch("shutil.disk_usage", return_value=(10 * (1024.0**3), 42, 42)):
        total = coresys.hardware.disk.get_disk_total_space("/data")

    assert total == 10.0


def test_used_space(coresys):
    """Test used space helper."""
    with patch("shutil.disk_usage", return_value=(42, 8 * (1024.0**3), 42)):
        used = coresys.hardware.disk.get_disk_used_space("/data")

    assert used == 8.0


def test_get_mountinfo(coresys):
    """Test mountinfo helper."""
    mountinfo = coresys.hardware.disk._get_mountinfo("/proc")
    assert mountinfo[4] == "/proc"


def test_get_mount_source(coresys):
    """Test mount source helper."""
    # For /proc the mount source is known to be "proc"...
    mount_source = coresys.hardware.disk._get_mount_source("/proc")
    assert mount_source == "proc"


def test_get_dir_structure_sizes(coresys, tmp_path):
    """Test directory structure size calculation."""
    # Create a test directory structure
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create some files
    (test_dir / "file1.txt").write_text("content1")
    (test_dir / "file2.txt").write_text("content2" * 100)  # Larger file

    # Create subdirectories
    subdir1 = test_dir / "subdir1"
    subdir1.mkdir()
    (subdir1 / "file3.txt").write_text("content3")

    subdir2 = test_dir / "subdir2"
    subdir2.mkdir()
    (subdir2 / "file4.txt").write_text("content4")

    # Create nested subdirectory
    nested_dir = subdir1 / "nested"
    nested_dir.mkdir()
    (nested_dir / "file5.txt").write_text("content5")

    # Create a symlink (should be skipped)
    (test_dir / "symlink.txt").symlink_to(test_dir / "file1.txt")

    # Test with max_depth=1 (default)
    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir, max_depth=1)

    # Verify the structure
    assert result["used_bytes"] > 0
    assert "children" not in result

    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir, max_depth=2)

    # Verify the structure
    assert result["used_bytes"] > 0
    assert "children" in result
    children = result["children"]

    # Should have subdir1 and subdir2, but not nested (due to max_depth=1)
    child_names = [child["id"] for child in children]
    assert "subdir1" in child_names
    assert "subdir2" in child_names
    assert "nested" not in child_names

    # Verify sizes are calculated correctly
    subdir1 = next(child for child in children if child["id"] == "subdir1")
    subdir2 = next(child for child in children if child["id"] == "subdir2")
    assert subdir1["used_bytes"] > 0
    assert subdir2["used_bytes"] > 0
    assert "children" not in subdir1  # No children due to max_depth=1
    assert "children" not in subdir2

    # Test with max_depth=2
    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir, max_depth=3)

    # Should now include nested directory
    child_names = [child["id"] for child in result["children"]]
    assert "subdir1" in child_names
    assert "subdir2" in child_names

    subdir1 = next(child for child in result["children"] if child["id"] == "subdir1")
    nested_children = [child["id"] for child in subdir1["children"]]
    assert "nested" in nested_children
    nested = next(child for child in subdir1["children"] if child["id"] == "nested")
    assert nested["used_bytes"] > 0

    # Test with max_depth=0 (should only count files in root, no children)
    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir, max_depth=0)
    assert result["used_bytes"] > 0
    assert "children" not in result  # No children due to max_depth=0


def test_get_dir_structure_sizes_empty_dir(coresys, tmp_path):
    """Test directory structure size calculation with empty directory."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    result = coresys.hardware.disk.get_dir_structure_sizes(empty_dir)

    assert result["used_bytes"] == 0
    assert "children" not in result


def test_get_dir_structure_sizes_nonexistent_dir(coresys, tmp_path):
    """Test directory structure size calculation with nonexistent directory."""
    nonexistent_dir = tmp_path / "nonexistent"

    result = coresys.hardware.disk.get_dir_structure_sizes(nonexistent_dir)

    assert result["used_bytes"] == 0
    assert "children" not in result


def test_get_dir_structure_sizes_only_files(coresys, tmp_path):
    """Test directory structure size calculation with only files (no subdirectories)."""
    files_dir = tmp_path / "files_dir"
    files_dir.mkdir()

    # Create some files
    (files_dir / "file1.txt").write_text("content1")
    (files_dir / "file2.txt").write_text("content2" * 50)

    result = coresys.hardware.disk.get_dir_structure_sizes(files_dir)

    assert result["used_bytes"] > 0
    assert "children" not in result  # No children since no subdirectories


def test_get_dir_structure_sizes_zero_size_children(coresys, tmp_path):
    """Test directory structure size calculation with zero-size children."""
    test_dir = tmp_path / "zero_size_test"
    test_dir.mkdir()

    # Create a file in root
    (test_dir / "file1.txt").write_text("content1")

    # Create an empty subdirectory
    empty_subdir = test_dir / "empty_subdir"
    empty_subdir.mkdir()

    # Create a subdirectory with content
    content_subdir = test_dir / "content_subdir"
    content_subdir.mkdir()
    (content_subdir / "file2.txt").write_text("content2")

    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir)

    # Should include content_subdir but not empty_subdir (since size > 0)
    assert result["used_bytes"] > 0
    assert "children" not in result


def test_try_get_emmc_life_time(coresys, tmp_path):
    """Test eMMC life time helper."""
    fake_life_time = tmp_path / "fake-mmcblk0-lifetime"
    fake_life_time.write_text("0x01 0x02\n")

    with patch(
        "supervisor.hardware.disk._BLOCK_DEVICE_EMMC_LIFE_TIME",
        str(tmp_path / "fake-{}-lifetime"),
    ):
        value = coresys.hardware.disk._try_get_emmc_life_time("mmcblk0")
    assert value == 10.0


def test_get_dir_structure_sizes_ebadmsg_error(coresys, tmp_path):
    """Test directory structure size calculation with EBADMSG error."""
    # Create a test directory structure
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()

    # Create some files
    (test_dir / "file1.txt").write_text("content1")

    # Create a subdirectory
    subdir = test_dir / "subdir"
    subdir.mkdir()
    (subdir / "file2.txt").write_text("content2")

    # Mock is_dir, is_symlink, and stat methods to handle the EBADMSG error correctly

    def mock_is_dir(self):
        # Use the real is_dir for all paths
        return os.path.isdir(self)

    def mock_is_symlink(self):
        # Use the real is_symlink for all paths
        return os.path.islink(self)

    def mock_stat_ebadmsg(self, follow_symlinks=True):
        # Raise EBADMSG for any child of test_dir to ensure consistent behavior
        if self.parent == test_dir:
            raise OSError(errno.EBADMSG, "Bad message")
        # For other paths, use the real os.stat
        return os.stat(self, follow_symlinks=follow_symlinks)

    with (
        patch.object(Path, "is_dir", mock_is_dir),
        patch.object(Path, "is_symlink", mock_is_symlink),
        patch.object(Path, "stat", mock_stat_ebadmsg),
    ):
        result = coresys.hardware.disk.get_dir_structure_sizes(test_dir)

    # The EBADMSG error should cause the loop to break on the first child
    # Since all children raise EBADMSG, we should get 0 used space
    assert result["used_bytes"] == 0
    assert "children" not in result

    # Verify that the unhealthy reason was added
    assert coresys.resolution.unhealthy
    assert UnhealthyReason.OSERROR_BAD_MESSAGE in coresys.resolution.unhealthy


async def test_try_get_nvme_life_time(
    coresys: CoreSys, nvme_data_disk: NVMeControllerService
):
    """Test getting lifetime info from an NVMe."""
    lifetime = await coresys.hardware.disk.get_disk_life_time(
        coresys.config.path_supervisor
    )
    assert lifetime == 1

    nvme_data_disk.smart_get_attributes_response["percent_used"].value = 50
    lifetime = await coresys.hardware.disk.get_disk_life_time(
        coresys.config.path_supervisor
    )
    assert lifetime == 50


async def test_try_get_nvme_life_time_missing_percent_used(
    coresys: CoreSys, nvme_data_disk: NVMeControllerService
):
    """Test getting lifetime info from an NVMe when percent_used is missing."""
    # Simulate a drive that doesn't provide percent_used
    nvme_data_disk.set_missing_attributes(["percent_used"])

    lifetime = await coresys.hardware.disk.get_disk_life_time(
        coresys.config.path_supervisor
    )
    assert lifetime is None


async def test_try_get_nvme_life_time_dbus_not_connected(coresys: CoreSys):
    """Test getting lifetime info from an NVMe when DBUS is not connected."""
    # Set the dbus for udisks2 bus to be None, to make it forcibly disconnected.
    coresys.dbus.udisks2.dbus = None

    lifetime = await coresys.hardware.disk.get_disk_life_time(
        coresys.config.path_supervisor
    )
    assert lifetime is None
