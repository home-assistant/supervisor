"""D-Bus interface for rauc."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_NAME = "de.pengutronix.rauc"
DBUS_OBJECT = "/"


class Rauc(DBusInterface):
    """Handle D-Bus interface for rauc."""

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to rauc")
        except DBusInterfaceError:
            _LOGGER.warning("Host have no rauc support. Disable OTA updates!")

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

    @dbus_connected
    def get_properties(self):
        """Return rauc informations.

        Return a coroutine.
        """
        return self.dbus.get_properties(f"{DBUS_NAME}.Installer")

    @dbus_connected
    def signal_completed(self):
        """Return a signal wrapper for completed signal.

        Return a coroutine.
        """
        return self.dbus.wait_signal(f"{DBUS_NAME}.Installer.Completed")
