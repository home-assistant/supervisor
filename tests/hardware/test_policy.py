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

    assert coresys.hardware.policy.get_cgroups_rule(device) == "c 5:* rwm"


def test_policy_group(coresys):
    """Test policy group generator."""
    assert coresys.hardware.policy.get_cgroups_rules(PolicyGroup.VIDEO) == [
        "c 239:* rwm",
        "c 29:* rwm",
    ]
