"""Test HardwareManager Module."""
from pathlib import Path

from supervisor.hardware.data import Device

# pylint: disable=protected-access


def test_initial_device_initialize(coresys):
    """Initialize the local hardware."""

    assert not coresys.hardware.devices

    coresys.hardware._import_devices()

    assert coresys.hardware.devices


def test_device_path_lookup(coresys):
    """Test device lookup."""
    for device in (
        Device("ttyACM0", Path("/dev/ttyACM0"), "tty", [], {"ID_VENDOR": "xy"}),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            "tty",
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"ID_VENDOR": "xy"},
        ),
        Device("ttyS0", Path("/dev/ttyS0"), "tty", [], {}),
        Device("video1", Path("/dev/video1"), "misc", [], {"ID_VENDOR": "xy"}),
    ):
        coresys.hardware.update_device(device)

    assert coresys.hardware.exists_device_node(Path("/dev/ttyACM0"))
    assert coresys.hardware.exists_device_node(Path("/dev/ttyS1"))
    assert coresys.hardware.exists_device_node(Path("/dev/ttyS0"))
    assert coresys.hardware.exists_device_node(Path("/dev/serial/by-id/xyx"))

    assert not coresys.hardware.exists_device_node(Path("/dev/ttyS2"))
    assert not coresys.hardware.exists_device_node(Path("/dev/ttyUSB1"))
