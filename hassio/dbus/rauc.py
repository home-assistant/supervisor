"""D-Bus interface for rauc."""
import logging
from pathlib import PurePath

from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = "de.pengutronix.rauc"
DBUS_OBJECT = "/"


class Rauc(DBusInterface):
    """Handle D-Bus interface for rauc."""

    dbus_name = "de.pengutronix.rauc"
    dbus_path = "/"
    dbus_interface = "de.pengutronix.rauc.Install"

    @dbus_connected
    def install(self, raucb_file: PurePath):
        """Install rauc bundle file."""
        return self.interface.call_install(str(raucb_file))

    @dbus_connected
    def get_slot_status(self):
        """Get slot status."""
        return self.interface.call_getslotstatus()

    @dbus_connected
    def signal_completed(self):
        """Return a signal wrapper for completed signal."""
        return self.dbus.wait_signal(f"{DBUS_NAME}.Installer.Completed")
