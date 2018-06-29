"""DBus interface for rauc."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError
from ..utils.gdbus import DBus

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = 'de.pengutronix.rauc'
DBUS_OBJECT = '/'


class Rauc(DBusInterface):
    """Handle DBus interface for rauc."""

    async def connect(self):
        """Connect do bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to rauc")

    @dbus_connected
    def install(self, raucb_file):
        """Install rauc bundle file.

        Return a coroutine.
        """
        return self.dbus.Installer.Install(raucb_file)

    @dbus_connected
    def get_slot_status(self):
        """Get slot status.

        Return a coroutine.
        """
        return self.dbus.Installer.GetSlotStatus()
