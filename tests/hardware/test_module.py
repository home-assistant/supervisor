"""Test HardwareManager Module."""

from pathlib import Path
import threading
from unittest.mock import AsyncMock, MagicMock, PropertyMock, patch

import pyudev

from supervisor.coresys import CoreSys
from supervisor.hardware.const import UdevSubsystem
from supervisor.hardware.data import Device

# pylint: disable=protected-access


def _udev_device(sys_name: str, device_node: str | None, sys_path: str) -> MagicMock:
    """Return a udev device as listed by pyudev."""
    udev = MagicMock(spec=pyudev.Device)
    udev.sys_name = sys_name
    udev.device_node = device_node
    udev.sys_path = sys_path
    udev.subsystem = "tty"
    udev.parent = None
    udev.device_links = []
    udev.properties = {}
    udev.children = []
    return udev


async def test_load_imports_devices_in_executor(coresys: CoreSys) -> None:
    """Test load reads the udev database without blocking the event loop."""
    assert not coresys.hardware.devices

    threads: list[threading.Thread] = []

    undecodable = _udev_device("bad", None, "/sys/devices/platform/bad")
    type(undecodable).device_node = PropertyMock(
        side_effect=UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
    )

    def _list_devices() -> list[pyudev.Device]:
        threads.append(threading.current_thread())
        return [
            _udev_device(
                "ttyUSB0", "/dev/ttyUSB0", "/sys/devices/platform/usb1/1-1/ttyUSB0"
            ),
            _udev_device("no_node", None, "/sys/devices/platform/no_node"),
            _udev_device("tty0", "/dev/tty0", "/sys/devices/virtual/tty/tty0"),
            undecodable,
        ]

    with (
        patch.object(coresys.hardware.udev, "list_devices", _list_devices),
        patch.object(coresys.hardware.helper, "load", AsyncMock()),
        patch.object(coresys.hardware.monitor, "load", AsyncMock()),
    ):
        await coresys.hardware.load()

    assert threads
    assert threading.main_thread() not in threads
    assert [device.name for device in coresys.hardware.devices] == ["ttyUSB0", "tun"]


def test_device_path_lookup(coresys):
    """Test device lookup."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/001"),
            "tty",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/000"),
            "tty",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/003"),
            "misc",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    assert coresys.hardware.exists_device_node(Path("/dev/ttyACM0"))
    assert coresys.hardware.exists_device_node(Path("/dev/ttyS1"))
    assert coresys.hardware.exists_device_node(Path("/dev/ttyS0"))
    assert coresys.hardware.exists_device_node(Path("/dev/serial/by-id/xyx"))
    assert coresys.hardware.exists_device_node(Path("/sys/bus/usb/001"))

    assert not coresys.hardware.exists_device_node(Path("/dev/ttyS2"))
    assert not coresys.hardware.exists_device_node(Path("/dev/ttyUSB1"))


def test_device_filter(coresys):
    """Test device filter."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/000"),
            "tty",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/001"),
            "tty",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/003"),
            "misc",
            None,
            [],
            {"ID_VENDOR": "xy"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    assert sorted(
        device.path for device in coresys.hardware.filter_devices()
    ) == sorted(device.path for device in coresys.hardware.devices)
    assert sorted(
        device.path
        for device in coresys.hardware.filter_devices(subsystem=UdevSubsystem.SERIAL)
    ) == sorted(
        device.path
        for device in coresys.hardware.devices
        if device.subsystem == UdevSubsystem.SERIAL
    )
