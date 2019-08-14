"""D-Bus interface for rauc."""
import logging

from cpe import CPE

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DBusError
from ..utils.gdbus import DBus
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER = logging.getLogger(__name__)

DBUS_NAME = "de.pengutronix.rauc"
DBUS_OBJECT = "/"


class Rauc(DBusInterface, CoreSysAttributes):
    """Handle D-Bus interface for rauc."""

    def __init__(self, coresys: CoreSys):
        """Initialize rauc D-Bus interface."""
        self.coresys: CoreSys = coresys
        super(Rauc, self).__init__()

    async def connect(self):
        """Connect to D-Bus."""
        try:
            assert self.sys_dbus.hostname.is_connected

            # Check if host is running HassOS
            assert self.sys_host.info.cpe is not None
            cpe = CPE(self.sys_host.info.cpe)
            assert cpe.get_product()[0] == "hassos"

            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to rauc")
        except (AssertionError, NotImplementedError):
            _LOGGER.debug("Found no HassOS, skipping connecting to rauc")

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
