"""Interface to Logind over D-Bus."""
import logging

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.dbus_next import DBus
from .const import DBUS_NAME_LOGIND, DBUS_OBJECT_LOGIND
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Logind(DBusInterface):
    """Logind function handler."""

    name = DBUS_NAME_LOGIND

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_LOGIND, DBUS_OBJECT_LOGIND)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd-logind")
        except DBusInterfaceError:
            _LOGGER.info("No systemd-logind support on the host.")

    @dbus_connected
    def reboot(self):
        """Reboot host computer.

        Return a coroutine.
        """
        return self.dbus.Manager.Reboot(False)

    @dbus_connected
    def power_off(self):
        """Power off host computer.

        Return a coroutine.
        """
        return self.dbus.Manager.PowerOff(False)
