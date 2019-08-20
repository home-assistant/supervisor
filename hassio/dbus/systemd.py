"""Interface to Systemd over D-Bus."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER = logging.getLogger(__name__)


class Systemd(DBusInterface):
    """Systemd function handler."""

    dbus_name = "org.freedesktop.systemd1"
    dbus_path = "/org/freedesktop/systemd1"
    dbus_interface = "org.freedesktop.systemd1.Manager"

    @dbus_connected
    def reboot(self):
        """Reboot host computer."""
        return self.interface.call_reboot()

    @dbus_connected
    def power_off(self):
        """Power off host computer."""
        return self.interface.call_poweroff()

    @dbus_connected
    def start_unit(self, unit: str, mode: str):
        """Start a systemd service unit."""
        return self.interface.call_startunit(unit, mode)

    @dbus_connected
    def stop_unit(self, unit: str, mode: str):
        """Stop a systemd service unit."""
        return self.interface.call_stopunit(unit, mode)

    @dbus_connected
    def reload_unit(self, unit: str, mode: str):
        """Reload a systemd service unit."""
        return self.interface.call_reloadorrestartunit(unit, mode)

    @dbus_connected
    def restart_unit(self, unit: str, mode: str):
        """Restart a systemd service unit."""
        return self.interface.call_restartunit(unit, mode)

    @dbus_connected
    def list_units(self):
        """Return a list of available systemd services."""
        return self.interface.call_listunits()
