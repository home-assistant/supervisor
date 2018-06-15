"""Service control for host."""
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import HassioError, HostNotSupportedError

_LOGGER = logging.getLogger(__name__)


class ServiceManager(CoreSysAttributes):
    """Handle local service information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys
        self._data = []

    def _check_dbus(self):
        """Check available dbus connection."""
        if self.sys_dbus.systemd.is_connected:
            return

        _LOGGER.error("No systemd dbus connection available")
        raise HostNotSupportedError()
    
    @property
    def services(self):
        """Return a list of local services."""
        return self._data

    async def update(self):
        """Update properties over dbus."""
        self._check_dbus()

        _LOGGER.info("Update service information")
        try:
            self._data = await self.sys_dbus.systemd.list_units()
        except HassioError:
            _LOGGER.warning("Can't update host service information!")
