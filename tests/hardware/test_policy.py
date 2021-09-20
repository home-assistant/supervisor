"""Test HardwareManager Module."""
from pathlib import Path

from supervisor.hardware.const import PolicyGroup
from supervisor.hardware.data import Device

# pylint: disable=protected-access


def test_device_policy(coresys):
    """Test device cgroup policy."""
    device = Device(
        "ttyACM0",
        Path("/dev/ttyACM0"),
        Path("/sys/bus/usb/001"),
        "tty",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10"},
        [],
    )

    assert coresys.hardware.policy.get_cgroups_rule(device) == "c 5:10 rwm"

    disk = Device(
        "sda0",
        Path("/dev/sda0"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10"},
        [],
    )

    assert coresys.hardware.policy.get_cgroups_rule(disk) == "b 5:10 rwm"


def test_policy_group(coresys):
    """Test policy group generator."""
    assert coresys.hardware.policy.get_cgroups_rules(PolicyGroup.VIDEO) == [
        "c 29:* rwm",
        "c 81:* rwm",
        "c 226:* rwm",
    ]


def test_device_in_policy(coresys):
    """Test device cgroup policy."""
    device = Device(
        "ttyACM0",
        Path("/dev/ttyACM0"),
        Path("/sys/bus/usb/001"),
        "tty",
        None,
        [],
        {"MAJOR": "204", "MINOR": "10"},
        [],
    )

    assert coresys.hardware.policy.is_match_cgroup(PolicyGroup.UART, device)
    assert not coresys.hardware.policy.is_match_cgroup(PolicyGroup.GPIO, device)


def test_allowed_access(coresys):
    """Test if is allow to access for device."""

    disk = Device(
        "sda0",
        Path("/dev/sda0"),
        Path("/sys/bus/usb/001"),
        "block",
        None,
        [],
        {"MAJOR": "5", "MINOR": "10", "ID_FS_LABEL": "hassos-overlay"},
        [],
    )

    assert not coresys.hardware.policy.allowed_for_access(disk)

    device = Device(
        "ttyACM0",
        Path("/dev/ttyACM0"),
        Path("/sys/bus/usb/001"),
        "tty",
        None,
        [],
        {"MAJOR": "204", "MINOR": "10"},
        [],
    )

    assert coresys.hardware.policy.allowed_for_access(device)


def test_dynamic_group_alloc_minor(coresys):
    """Test dynamic cgroup generation based on minor."""
    for device in (
        Device(
            "ttyACM0",
            Path("/dev/ttyACM0"),
            Path("/sys/bus/usb/001"),
            "tty",
            None,
            [],
            {"MAJOR": "204", "MINOR": "10"},
            [],
        ),
        Device(
            "ttyUSB0",
            Path("/dev/ttyUSB0"),
            Path("/sys/bus/usb/000"),
            "tty",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"MAJOR": "188", "MINOR": "10"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {"MAJOR": "4", "MINOR": "65"},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/003"),
            "misc",
            None,
            [],
            {"MAJOR": "38", "MINOR": "10"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    assert coresys.hardware.policy.get_cgroups_rules(PolicyGroup.UART) == [
        "c 204:* rwm",
        "c 188:* rwm",
        "c 166:* rwm",
        "c 4:65 rwm",
    ]


def test_dynamic_group_alloc_major(coresys):
    """Test dynamic cgroup generation based on minor."""
    for device in (
        Device(
            "gpio16",
            Path("/dev/gpio16"),
            Path("/sys/bus/usb/001"),
            "gpio",
            None,
            [],
            {"MAJOR": "254", "MINOR": "10"},
            [],
        ),
        Device(
            "gpiomem",
            Path("/dev/gpiomem"),
            Path("/sys/bus/usb/000"),
            "gpiomem",
            None,
            [Path("/dev/ttyS1"), Path("/dev/serial/by-id/xyx")],
            {"MAJOR": "239", "MINOR": "10"},
            [],
        ),
        Device(
            "ttyS0",
            Path("/dev/ttyS0"),
            Path("/sys/bus/usb/002"),
            "tty",
            None,
            [],
            {"MAJOR": "4", "MINOR": "65"},
            [],
        ),
        Device(
            "video1",
            Path("/dev/video1"),
            Path("/sys/bus/usb/003"),
            "misc",
            None,
            [],
            {"MAJOR": "38", "MINOR": "10"},
            [],
        ),
    ):
        coresys.hardware.update_device(device)

    assert coresys.hardware.policy.get_cgroups_rules(PolicyGroup.GPIO) == [
        "c 254:* rwm",
        "c 239:* rwm",
    ]
