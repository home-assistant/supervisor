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
        [],
        {"MAJOR": "5", "MINOR": "10"},
    )

    assert coresys.hardware.policy.get_cgroups_rule(device) == "c 5:10 rwm"

    disk = Device(
        "sda0",
        Path("/dev/sda0"),
        Path("/sys/bus/usb/001"),
        "block",
        [],
        {"MAJOR": "5", "MINOR": "10"},
    )

    assert coresys.hardware.policy.get_cgroups_rule(disk) == "b 5:10 rwm"


def test_policy_group(coresys):
    """Test policy group generator."""
    assert coresys.hardware.policy.get_cgroups_rules(PolicyGroup.VIDEO) == [
        "c 239:* rwm",
        "c 29:* rwm",
        "c 81:* rwm",
        "c 251:* rwm",
        "c 242:* rwm",
        "c 226:* rwm",
    ]


def test_device_in_policy(coresys):
    """Test device cgroup policy."""
    device = Device(
        "ttyACM0",
        Path("/dev/ttyACM0"),
        Path("/sys/bus/usb/001"),
        "tty",
        [],
        {"MAJOR": "204", "MINOR": "10"},
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
        [],
        {"MAJOR": "5", "MINOR": "10", "ID_FS_LABEL": "hassos-overlay"},
    )

    assert not coresys.hardware.policy.allowed_for_access(disk)

    device = Device(
        "ttyACM0",
        Path("/dev/ttyACM0"),
        Path("/sys/bus/usb/001"),
        "tty",
        [],
        {"MAJOR": "204", "MINOR": "10"},
    )

    assert coresys.hardware.policy.allowed_for_access(device)
