"""DBus interface for hostname."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError
from ..utils.gdbus import DBus

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = 'org.freedesktop.hostname1'
DBUS_OBJECT = '/org/freedesktop/hostname1'


class Hostname(DBusInterface):
    """Handle DBus interface for hostname/system."""

    async def connect(self):
        """Connect do bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to hostname")

    @dbus_connected
    def set_static_hostname(self, hostname):
        """Change local hostname.

        Return a coroutine.
        """
        return self.dbus.SetStaticHostname(hostname, False)

    @dbus_connected
    def get_properties(self):
        """Return local host informations.

        Return a coroutine.
        """
        return self.dbus.get_properties(DBUS_NAME)
