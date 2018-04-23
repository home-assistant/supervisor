"""Interface to Systemd over dbus."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError
from ..utils.gdbus import DBus

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = 'org.freedesktop.systemd1'
DBUS_OBJECT = '/org/freedesktop/systemd1'


class Systemd(DBusInterface):
    """Systemd function handler."""

    async def connect(self):
        """Connect do bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd")

    @dbus_connected
    def reboot(self):
        """Reboot host computer.

        Return a coroutine.
        """
        return self.dbus.Manager.Reboot()

    @dbus_connected
    def power_off(self):
        """Power off host computer.

        Return a coroutine.
        """
        return self.dbus.Manager.PowerOff()
