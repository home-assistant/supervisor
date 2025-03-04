"""Test hardware utils."""

import errno
from pathlib import Path
from unittest.mock import MagicMock, patch

from pytest import LogCaptureFixture

from supervisor.coresys import CoreSys
from supervisor.hardware.data import Device


def test_have_audio(coresys: CoreSys):
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


def test_have_usb(coresys: CoreSys):
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


def test_have_gpio(coresys: CoreSys):
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


def test_hide_virtual_device(coresys: CoreSys):
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


async def test_last_boot_error(coresys: CoreSys, caplog: LogCaptureFixture):
    """Test error reading last boot."""
    with patch(
        "supervisor.hardware.helper.Path.read_text", side_effect=(err := OSError())
    ):
        err.errno = errno.EBADMSG
        assert await coresys.hardware.helper.last_boot() is None

        assert coresys.core.healthy is True
        assert "Can't read stat data" in caplog.text
