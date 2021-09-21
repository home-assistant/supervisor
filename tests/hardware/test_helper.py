"""Test hardware utils."""
# pylint: disable=protected-access
from pathlib import Path
from unittest.mock import MagicMock

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
            None,
            [],
            {"ID_NAME": "xy"},
            [],
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
            None,
            [],
            {"ID_NAME": "xy"},
            [],
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
            None,
            [],
            {"ID_NAME": "xy"},
            [],
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
