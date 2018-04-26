"""Power control for host."""
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import HassioError, HostNotSupportedError

_LOGGER = logging.getLogger(__name__)

UNKNOWN = 'Unknown'


class InfoCenter(CoreSysAttributes):
    """Handle local system information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys
        self._data = {}

    @property
    def hostname(self):
        """Return local hostname."""
        return self._data.get('Hostname', UNKNOWN)

    @property
    def chassis(self):
        """Return local chassis type."""
        return self._data.get('Chassis', UNKNOWN)

    @property
    def kernel(self):
        """Return local kernel version."""
        return self._data.get('KernelRelease', UNKNOWN)

    @property
    def operating_system(self):
        """Return local operating system."""
        return self._data.get('OperatingSystemPrettyName', UNKNOWN)

    @property
    def cpe(self):
        """Return local CPE."""
        return self._data.get('OperatingSystemCPEName', UNKNOWN)

    def _check_dbus_hostname(self):
        """Check if systemd is connect or raise error."""
        if not self.sys_dbus.hostname.is_connected:
            _LOGGER.error("No hostname dbus connection available")
            raise HostNotSupportedError()

    async def update(self):
        """Update properties over dbus."""
        self._check_dbus_hostname()

        _LOGGER.info("Update local host information")
        try:
            self._data = await self.sys_dbus.hostname.get_properties()
        except HassioError:
            _LOGGER.warning("Can't update host system information!")
