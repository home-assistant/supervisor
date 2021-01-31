"""Test hardware utils."""
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_have_usb(coresys):
    """Test usb device filter."""
    assert not coresys.hardware.helper.support_usb

    coresys.hardware.update_device(
        Device(
            "sda",
            Path("/dev/sda"),
            Path("/sys/bus/usb/000"),
            "usb",
            [],
            {"ID_NAME": "xy"},
        )
    )

    assert coresys.hardware.helper.support_usb


def test_have_gpio(coresys):
    """Test usb device filter."""
    assert not coresys.hardware.helper.support_gpio

    coresys.hardware.update_device(
        Device(
            "sda",
            Path("/dev/sda"),
            Path("/sys/bus/usb/000"),
            "gpio",
            [],
            {"ID_NAME": "xy"},
        )
    )

    assert coresys.hardware.helper.support_gpio


def test_hide_virtual_device(coresys):
    """Test hidding virtual devices."""
    udev_device = MagicMock()

    udev_device.sys_path = "/sys/devices/platform/test"
    assert not coresys.hardware.helper.hide_virtual_device(udev_device)

    udev_device.sys_path = "/sys/devices/virtual/block/test"
    assert coresys.hardware.helper.hide_virtual_device(udev_device)

    udev_device.sys_path = "/sys/devices/virtual/tty/tty1"
    assert coresys.hardware.helper.hide_virtual_device(udev_device)

    udev_device.sys_path = "/sys/devices/virtual/vc/vcs1"
    assert coresys.hardware.helper.hide_virtual_device(udev_device)


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
