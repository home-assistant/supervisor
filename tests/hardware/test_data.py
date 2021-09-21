"""Test HardwareManager Module."""
from pathlib import Path

from supervisor.hardware.data import Device

# pylint: disable=protected-access


def test_device_property(coresys):
    """Test device cgroup policy."""
    device = Device(
        "ttyACM0",
        Path("/dev/ttyACM0"),
        Path("/sys/bus/usb/001"),
        "tty",
        None,
        [Path("/dev/serial/by-id/fixed-device")],
        {"MAJOR": "5", "MINOR": "10"},
        [],
    )

    assert device.by_id == device.links[0]
    assert device.major == 5
    assert device.minor == 10
