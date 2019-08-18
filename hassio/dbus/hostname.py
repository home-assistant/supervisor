"""D-Bus interface for hostname."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError
from ..utils.gdbus import DBus

_LOGGER = logging.getLogger(__name__)


class Hostname(DBusInterface):
    """Handle D-Bus interface for hostname/system."""

    dbus_name = "org.freedesktop.hostname1"
    dbus_path = "/org/freedesktop/hostname1"
    dbus_interface = "/org/freedesktop/hostname1"
    interface_property = [""]

    @dbus_connected
    def set_static_hostname(self, hostname):
        """Change local hostname.

        Return a coroutine.
        """
        return self.interface.call_setstatichostname(hostname, False)

    @dbus_connected
    def get_properties(self):
        """Return local host informations.

        Return a coroutine.
        """
        return self.dbus.get_properties(DBUS_NAME)
