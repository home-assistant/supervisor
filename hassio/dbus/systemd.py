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

    @dbus_connected
    def start_unit(self, unit):
        """Start a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.StartUnit(unit)

    @dbus_connected
    def stop_unit(self, unit):
        """Stop a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.StopUnit(unit)

    @dbus_connected
    def reload_unit(self, unit):
        """Reload a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.ReloadOrRestartUnit(unit)

    @dbus_connected
    def restart_unit(self, unit):
        """Restart a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.RestartUnit(unit)

    @dbus_connected
    def list_units(self):
        """Return a list of available systemd services.

        Return a coroutine.
        """
        return self.dbus.Manager.ListUnits()
