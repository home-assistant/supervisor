"""D-Bus interface for hostname."""
import logging
from typing import Optional

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_NAME = "org.freedesktop.hostname1"
DBUS_OBJECT = "/org/freedesktop/hostname1"


class Hostname(DBusInterface):
    """Handle D-Bus interface for hostname/system."""

    def __init__(self):
        """Initialize Properties."""
        self._hostname: Optional[str] = None
        self._chassis: Optional[str] = None
        self._deployment: Optional[str] = None
        self._kernel: Optional[str] = None
        self._operating_system: Optional[str] = None
        self._cpe: Optional[str] = None

    async def connect(self):
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to hostname")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No hostname support on the host. Hostname functions have been disabled."
            )

    @property
    def hostname(self) -> Optional[str]:
        """Return local hostname."""
        return self._hostname

    @property
    def chassis(self) -> Optional[str]:
        """Return local chassis type."""
        return self._chassis

    @property
    def deployment(self) -> Optional[str]:
        """Return local deployment type."""
        return self._deployment

    @property
    def kernel(self) -> Optional[str]:
        """Return local kernel version."""
        return self._kernel

    @property
    def operating_system(self) -> Optional[str]:
        """Return local operating system."""
        return self._operating_system

    @property
    def cpe(self) -> Optional[str]:
        """Return local CPE."""
        return self._cpe

    @dbus_connected
    def set_static_hostname(self, hostname):
        """Change local hostname.

        Return a coroutine.
        """
        return self.dbus.SetStaticHostname(hostname, False)

    @dbus_connected
    async def update(self):
        """Update Properties."""
        data = await self.dbus.get_properties(DBUS_NAME)
        if not data:
            _LOGGER.warning("Can't get properties for Hostname")
            return

        self._hostname = data.get("StaticHostname")
        self._chassis = data.get("Chassis")
        self._deployment = data.get("Deployment")
        self._kernel = data.get("KernelRelease")
        self._operating_system = data.get("OperatingSystemPrettyName")
        self._cpe = data.get("OperatingSystemCPEName")
