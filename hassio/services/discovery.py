"""Handle discover message for Home-Assistant."""
import logging

from ..coresys import CoreSysAttributes


class Discovery(CoreSysAttributes):
    """Home-Assistant Discovery handler."""

    def __init__(self, coresys):
        """Initialize discovery handler."""
        self.coresys = coresys

    @property
    def _data(self):
        """Return discovery data."""
        return self._services.data.discovery
