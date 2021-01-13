"""Test hardware utils."""
from pathlib import Path
from unittest.mock import patch

from supervisor.hardware.data import Device


def test_video_devices(coresys):
    """Test video device filter."""
    for device in (
        Device("test-dev", Path("/dev/test-dev"), "xy", [], {}),
        Device("vchiq", Path("/dev/vchiq"), "xy", [], {}),
        Device("cec0", Path("/dev/cec0"), "xy", [], {}),
        Device("video1", Path("/dev/video1"), "xy", [], {}),
    ):
        coresys.hardware.update_device(device)

    assert [device.name for device in coresys.hardware.helper.video_devices] == [
        "vchiq",
        "cec0",
        "video1",
    ]


def test_serial_devices(coresys):
    """Test serial device filter."""
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

    assert [
        (device.name, device.links) for device in coresys.hardware.helper.serial_devices
    ] == [
        ("ttyACM0", []),
        ("ttyUSB0", [Path("/dev/serial/by-id/xyx")]),
        ("ttyS0", []),
    ]


def test_usb_devices(coresys):
    """Test usb device filter."""
    for device in (
        Device("usb1", Path("/dev/bus/usb/1/1"), "usb", [], {}),
        Device("usb2", Path("/dev/bus/usb/2/1"), "usb", [], {}),
        Device("cec0", Path("/dev/cec0"), "xy", [], {}),
        Device("video1", Path("/dev/video1"), "xy", [], {}),
    ):
        coresys.hardware.update_device(device)

    assert [device.name for device in coresys.hardware.helper.usb_devices] == [
        "usb1",
        "usb2",
    ]


def test_block_devices(coresys):
    """Test usb device filter."""
    for device in (
        Device("sda", Path("/dev/sda"), "block", [], {"ID_NAME": "xy"}),
        Device("sdb", Path("/dev/sdb"), "block", [], {"ID_NAME": "xy"}),
        Device("cec0", Path("/dev/cec0"), "xy", [], {}),
        Device("video1", Path("/dev/video1"), "xy", [], {"ID_NAME": "xy"}),
    ):
        coresys.hardware.update_device(device)

    assert [device.name for device in coresys.hardware.helper.disk_devices] == [
        "sda",
        "sdb",
    ]


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
