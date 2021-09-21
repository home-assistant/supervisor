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
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        free = coresys.hardware.disk.get_disk_free_space("/data")

    assert free == 2.0


def test_total_space(coresys):
    """Test total space helper."""
    with patch("shutil.disk_usage", return_value=(10 * (1024.0 ** 3), 42, 42)):
        total = coresys.hardware.disk.get_disk_total_space("/data")

    assert total == 10.0


def test_used_space(coresys):
    """Test used space helper."""
    with patch("shutil.disk_usage", return_value=(42, 8 * (1024.0 ** 3), 42)):
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
