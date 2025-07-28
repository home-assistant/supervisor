"""Test hardware utils."""

# pylint: disable=protected-access
from pathlib import Path
from unittest.mock import patch

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device


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
    assert result["size"] > 0
    assert "children" in result
    children = result["children"]

    # Should have subdir1 and subdir2, but not nested (due to max_depth=1)
    assert "subdir1" in children
    assert "subdir2" in children
    assert "nested" not in children

    # Verify sizes are calculated correctly
    assert children["subdir1"]["size"] > 0
    assert children["subdir2"]["size"] > 0
    assert "children" not in children["subdir1"]  # No children due to max_depth=1
    assert "children" not in children["subdir2"]

    # Test with max_depth=2
    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir, max_depth=2)

    # Should now include nested directory
    assert "subdir1" in result["children"]
    assert "subdir2" in result["children"]
    assert "nested" in result["children"]["subdir1"]["children"]
    assert result["children"]["subdir1"]["children"]["nested"]["size"] > 0

    # Test with max_depth=0 (should only count files in root, no children)
    result = coresys.hardware.disk.get_dir_structure_sizes(test_dir, max_depth=0)
    assert result["size"] > 0
    assert "children" not in result  # No children due to max_depth=0


def test_get_dir_structure_sizes_empty_dir(coresys, tmp_path):
    """Test directory structure size calculation with empty directory."""
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir()

    result = coresys.hardware.disk.get_dir_structure_sizes(empty_dir)

    assert result["size"] == 0
    assert "children" not in result


def test_get_dir_structure_sizes_nonexistent_dir(coresys, tmp_path):
    """Test directory structure size calculation with nonexistent directory."""
    nonexistent_dir = tmp_path / "nonexistent"

    result = coresys.hardware.disk.get_dir_structure_sizes(nonexistent_dir)

    assert result["size"] == 0
    assert "children" not in result


def test_get_dir_structure_sizes_only_files(coresys, tmp_path):
    """Test directory structure size calculation with only files (no subdirectories)."""
    files_dir = tmp_path / "files_dir"
    files_dir.mkdir()

    # Create some files
    (files_dir / "file1.txt").write_text("content1")
    (files_dir / "file2.txt").write_text("content2" * 50)

    result = coresys.hardware.disk.get_dir_structure_sizes(files_dir)

    assert result["size"] > 0
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
    assert result["size"] > 0
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
    assert value == 20.0
