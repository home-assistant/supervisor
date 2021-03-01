"""Policy / cgroups management of local host."""
import logging
from typing import Dict, List

from ..coresys import CoreSys, CoreSysAttributes
from .const import PolicyGroup, UdevSubsystem
from .data import Device

_LOGGER: logging.Logger = logging.getLogger(__name__)


# fmt: off
# https://www.kernel.org/doc/Documentation/admin-guide/devices.txt

_CGROUPS: Dict[PolicyGroup, List[int]] = {
    PolicyGroup.UART: [
        204,  # ttyAMA / ttySAC (tty)
        188,  # ttyUSB (tty)
        166   # ttyACM (tty)
    ],
    PolicyGroup.GPIO: [
        254,  # gpiochip (gpio)
        245   # gpiomem (gpiomem)
    ],
    PolicyGroup.VIDEO: [
        29,   # /dev/fb (graphics)
        81,
        226
    ],
    PolicyGroup.AUDIO: [
        116   # /dev/snd (sound)
    ],
    PolicyGroup.USB: [
        189,  # /dev/bus/usb (usb)
        180,  # hiddev (usbmisc)
    ],
    PolicyGroup.BLUETOOTH: [
        13    # /dev/input (input)
    ]
}

_CGROUPS_DYNAMIC_MAJOR: Dict[PolicyGroup, List[UdevSubsystem]] = {
    PolicyGroup.USB: [
        UdevSubsystem.HIDRAW
    ],
    PolicyGroup.GPIO: [
        UdevSubsystem.GPIO,
        UdevSubsystem.GPIOMEM
    ],
    PolicyGroup.VIDEO: [
        UdevSubsystem.VCHIQ,
        UdevSubsystem.MEDIA,
        UdevSubsystem.CEC,
        UdevSubsystem.RPI_H264MEM,
        UdevSubsystem.RPI_HEVCMEM
    ]
}

_CGROUPS_DYNAMIC_MINOR: Dict[PolicyGroup, List[UdevSubsystem]] = {
    PolicyGroup.UART: [
        UdevSubsystem.SERIAL
    ]
}

# fmt: on


class HwPolicy(CoreSysAttributes):
    """Handle Hardware policy / cgroups."""

    def __init__(self, coresys: CoreSys):
        """Init hardware policy object."""
        self.coresys = coresys

    def is_match_cgroup(self, group: PolicyGroup, device: Device) -> bool:
        """Return true if device is in cgroup Policy."""
        return device.cgroups_major in _CGROUPS.get(group, [])

    def get_cgroups_rules(self, group: PolicyGroup) -> List[str]:
        """Generate cgroups rules for a policy group."""
        cgroups: List[str] = [f"c {dev}:* rwm" for dev in _CGROUPS[group]]

        # Lookup dynamic device groups from host
        if group in _CGROUPS_DYNAMIC_MAJOR:
            majors = {
                device.major
                for device in self.sys_hardware.devices
                if device.subsystem in _CGROUPS_DYNAMIC_MAJOR[group]
                and device.cgroups_major not in _CGROUPS[group]
            }
            cgroups.extend([f"c {dev}:* rwm" for dev in majors])

        # Lookup dynamic devices from host
        if group in _CGROUPS_DYNAMIC_MINOR:
            for device in self.sys_hardware.devices:
                if (
                    device.subsystem not in _CGROUPS_DYNAMIC_MINOR[group]
                    or device.cgroups_major in _CGROUPS[group]
                ):
                    continue
                cgroups.append(self.get_cgroups_rule(device))

        return cgroups

    def get_cgroups_rule(self, device: Device) -> str:
        """Generate a cgroups rule for given device."""
        cgroup_type = "c" if device.subsystem != UdevSubsystem.DISK else "b"
        return f"{cgroup_type} {device.cgroups_major}:{device.cgroups_minor} rwm"

    def get_full_access(self) -> str:
        """Get full access to all devices."""
        return "a *:* rwm"

    def allowed_for_access(self, device: Device) -> bool:
        """Return True if allow to access to this device."""
        if self.sys_hardware.disk.is_system_partition(device):
            return False

        return True
