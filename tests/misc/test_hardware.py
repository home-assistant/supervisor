"""Test hardware utils."""
from pathlib import Path
from unittest.mock import PropertyMock, patch

from supervisor.misc.hardware import Device, Hardware


def test_read_all_devices():
    """Test to read all devices."""
    system = Hardware()

    assert system.devices


def test_video_devices():
    """Test video device filter."""
    system = Hardware()
    device_list = [
        Device("test-dev", Path("/dev/test-dev"), []),
        Device("vchiq", Path("/dev/vchiq"), []),
        Device("cec0", Path("/dev/cec0"), []),
        Device("video1", Path("/dev/video1"), []),
    ]

    with patch(
        "supervisor.misc.hardware.Hardware.devices", new_callable=PropertyMock
    ) as mock_device:
        mock_device.return_value = device_list

        assert system.video_devices == [
            Device("vchiq", Path("/dev/vchiq"), []),
            Device("cec0", Path("/dev/cec0"), []),
            Device("video1", Path("/dev/video1"), []),
        ]
