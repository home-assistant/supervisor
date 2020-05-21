"""Interface to Systemd over D-Bus."""
import logging

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_NAME = "org.freedesktop.systemd1"
DBUS_OBJECT = "/org/freedesktop/systemd1"


class Systemd(DBusInterface):
    """Systemd function handler."""

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to systemd")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No systemd support on the host. Host control has been disabled."
            )

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
    def start_unit(self, unit, mode):
        """Start a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.StartUnit(unit, mode)

    @dbus_connected
    def stop_unit(self, unit, mode):
        """Stop a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.StopUnit(unit, mode)

    @dbus_connected
    def reload_unit(self, unit, mode):
        """Reload a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.ReloadOrRestartUnit(unit, mode)

    @dbus_connected
    def restart_unit(self, unit, mode):
        """Restart a systemd service unit.

        Return a coroutine.
        """
        return self.dbus.Manager.RestartUnit(unit, mode)

    @dbus_connected
    def list_units(self):
        """Return a list of available systemd services.

        Return a coroutine.
        """
        return self.dbus.Manager.ListUnits()
