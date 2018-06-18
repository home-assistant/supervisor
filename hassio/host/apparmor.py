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

    @property
    def available(self):
        """Return True if AppArmor is availabe on host."""
        return self.available
