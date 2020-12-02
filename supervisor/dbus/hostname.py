"""D-Bus interface for hostname."""
import logging
from typing import Optional

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus
from .const import (
    DBUS_ATTR_CHASSIS,
    DBUS_ATTR_DEPLOYMENT,
    DBUS_ATTR_KERNEL_RELEASE,
    DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME,
    DBUS_ATTR_STATIC_HOSTNAME,
    DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME,
    DBUS_NAME_HOSTNAME,
    DBUS_OBJECT_HOSTNAME,
)
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Hostname(DBusInterface):
    """Handle D-Bus interface for hostname/system."""

    name = DBUS_NAME_HOSTNAME

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
            self.dbus = await DBus.connect(DBUS_NAME_HOSTNAME, DBUS_OBJECT_HOSTNAME)
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
        data = await self.dbus.get_properties(DBUS_NAME_HOSTNAME)
        if not data:
            _LOGGER.warning("Can't get properties for Hostname")
            return

        self._hostname = data.get(DBUS_ATTR_STATIC_HOSTNAME)
        self._chassis = data.get(DBUS_ATTR_CHASSIS)
        self._deployment = data.get(DBUS_ATTR_DEPLOYMENT)
        self._kernel = data.get(DBUS_ATTR_KERNEL_RELEASE)
        self._operating_system = data.get(DBUS_ATTR_OPERATING_SYSTEM_PRETTY_NAME)
        self._cpe = data.get(DBUS_ATTR_STATIC_OPERATING_SYSTEM_CPE_NAME)
