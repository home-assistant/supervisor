"""AppArmor control for host."""
import logging

from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class AppArmorControl(CoreSysAttributes):
    """Handle host apparmor controls."""

    def __init__(self, coresys):
        """Initialize host power handling."""
        self.coresys = coresys
        self._available = False
        self._profiles = set()

    @property
    def available(self):
        """Return True if AppArmor is availabe on host."""
        return self.available

    async def load_profile(self, profile_name, profile_file):
        """Load a new profile into AppArmor."""
    
    async def remove_profile(self, profile_name):
        """Remove a AppArmor profile."""
