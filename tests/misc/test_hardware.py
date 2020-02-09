"""Test hardware utils."""

from hassio.misc.hardware import Hardware


def test_read_all_devices():
    """Test to read all devices."""
    system = Hardware()

    assert system.devices
