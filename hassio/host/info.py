"""Info control for host."""
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import HassioError, HostNotSupportedError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class InfoCenter(CoreSysAttributes):
    """Handle local system information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys
        self._data = {}

    @property
    def hostname(self):
        """Return local hostname."""
        return self._data.get("StaticHostname") or None

    @property
    def chassis(self):
        """Return local chassis type."""
        return self._data.get("Chassis") or None

    @property
    def deployment(self):
        """Return local deployment type."""
        return self._data.get("Deployment") or None

    @property
    def kernel(self):
        """Return local kernel version."""
        return self._data.get("KernelRelease") or None

    @property
    def operating_system(self):
        """Return local operating system."""
        return self._data.get("OperatingSystemPrettyName") or None

    @property
    def cpe(self):
        """Return local CPE."""
        return self._data.get("OperatingSystemCPEName") or None

    async def update(self):
        """Update properties over dbus."""
        if not self.sys_dbus.hostname.is_connected:
            _LOGGER.error("No hostname D-Bus connection available")
            raise HostNotSupportedError()

        _LOGGER.info("Update local host information")
        try:
            self._data = await self.sys_dbus.hostname.get_properties()
        except HassioError:
            _LOGGER.warning("Can't update host system information!")
