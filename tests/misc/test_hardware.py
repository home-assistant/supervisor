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
        Device("test-dev", Path("/dev/test-dev"), "xy", [], {}),
        Device("vchiq", Path("/dev/vchiq"), "xy", [], {}),
        Device("cec0", Path("/dev/cec0"), "xy", [], {}),
        Device("video1", Path("/dev/video1"), "xy", [], {}),
    ]

    with patch(
        "supervisor.misc.hardware.Hardware.devices", new_callable=PropertyMock
    ) as mock_device:
        mock_device.return_value = device_list

        assert [device.name for device in system.video_devices] == [
            "vchiq",
            "cec0",
            "video1",
        ]


def test_serial_devices():
    """Test serial device filter."""
    system = Hardware()
    device_list = [
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
    ]

    with patch(
        "supervisor.misc.hardware.Hardware.devices", new_callable=PropertyMock
    ) as mock_device:
        mock_device.return_value = device_list

        assert [(device.name, device.links) for device in system.serial_devices] == [
            ("ttyACM0", []),
            ("ttyUSB0", [Path("/dev/serial/by-id/xyx")]),
        ]


def test_free_space():
    """Test free space helper."""
    system = Hardware()
    with patch("shutil.disk_usage", return_value=(42, 42, 2 * (1024.0 ** 3))):
        free = system.get_disk_free_space("/data")

    assert free == 2.0


def test_total_space():
    """Test total space helper."""
    system = Hardware()
    with patch("shutil.disk_usage", return_value=(10 * (1024.0 ** 3), 42, 42)):
        total = system.get_disk_total_space("/data")

    assert total == 10.0


def test_used_space():
    """Test used space helper."""
    system = Hardware()
    with patch("shutil.disk_usage", return_value=(42, 8 * (1024.0 ** 3), 42)):
        used = system.get_disk_used_space("/data")

    assert used == 8.0
