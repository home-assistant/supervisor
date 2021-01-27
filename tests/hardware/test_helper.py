"""Test hardware utils."""
from pathlib import Path
from unittest.mock import patch

from supervisor.hardware.data import Device


def test_have_audio(coresys):
    """Test usb device filter."""
    assert not coresys.hardware.helper.support_audio

    coresys.hardware.update_device(
        Device(
            "sda",
            Path("/dev/sda"),
            Path("/sys/bus/usb/000"),
            "sound",
            [],
            {"ID_NAME": "xy"},
        )
    )

    assert coresys.hardware.helper.support_audio


def test_free_space(coresys):
    """Test free space helper."""
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        free = coresys.hardware.helper.get_disk_free_space("/data")

    assert free == 2.0


def test_total_space(coresys):
    """Test total space helper."""
    with patch("shutil.disk_usage", return_value=(10 * (1024.0 ** 3), 42, 42)):
        total = coresys.hardware.helper.get_disk_total_space("/data")

    assert total == 10.0


def test_used_space(coresys):
    """Test used space helper."""
    with patch("shutil.disk_usage", return_value=(42, 8 * (1024.0 ** 3), 42)):
        used = coresys.hardware.helper.get_disk_used_space("/data")

    assert used == 8.0
