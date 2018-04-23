"""Interface to Systemd over dbus."""
import logging

from .utils import dbus_connected
from ..exceptions import DBusError
from ..utils.gdbus import DBus

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = 'org.freedesktop.systemd1'
DBUS_OBJECT = '/org/freedesktop/systemd1'


class Systemd:
    """Systemd function handler."""

    def __init__(self):
        """Initialize systemd."""
        self.dbus = None

    @property
    def is_connected(self):
        """Return True, if they is connected to dbus."""
        return self.dbus is not None

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
