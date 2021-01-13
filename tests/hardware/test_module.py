"""Test HardwareManager Module."""

# pylint: disable=protected-access


def test_initial_device_initialize(coresys):
    """Initialize the local hardware."""

    assert not coresys.hardware.devices

    coresys.hardware._import_devices()

    assert coresys.hardware.devices
