"""Policy / cgroups management of local host."""
import logging
from typing import Dict, List

from ..coresys import CoreSys, CoreSysAttributes
from .const import PolicyGroup
from .data import Device

_LOGGER: logging.Logger = logging.getLogger(__name__)


GROUP_CGROUPS: Dict[PolicyGroup, List[int]] = {
    PolicyGroup.UART: [204, 188, 166, 244],
    PolicyGroup.GPIO: [254],
    PolicyGroup.VIDEO: [239, 29],
    PolicyGroup.AUDIO: [116],
}


class HwPolicy(CoreSysAttributes):
    """Handle Hardware policy / cgroups."""

    def __init__(self, coresys: CoreSys):
        """Init hardware policy object."""
        self.coresys = coresys

    def get_cgroups_rules(self, group: PolicyGroup) -> List[str]:
        """Generate cgroups rules for a policy group."""
        return [f"c {dev}:* rwm" for dev in GROUP_CGROUPS.get(group, [])]

    def get_cgroups_rule(self, device: Device) -> str:
        """Generate a cgroups rule for given device."""
        return f"c {device.cgroups_major}:* rwm"
