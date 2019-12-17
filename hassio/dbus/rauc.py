"""D-Bus interface for rauc."""
import logging
from typing import Optional

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_NAME = "de.pengutronix.rauc"
DBUS_OBJECT = "/"


class Rauc(DBusInterface):
    """Handle D-Bus interface for rauc."""

    def __init__(self):
        """Initialize Properties."""
        self._operation: Optional[str] = None
        self._last_error: Optional[str] = None
        self._compatible: Optional[str] = None
        self._variant: Optional[str] = None
        self._boot_slot: Optional[str] = None

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to rauc")
        except DBusInterfaceError:
            _LOGGER.warning("Host has no rauc support. OTA updates have been disabled.")

    @property
    def operation(self) -> Optional[str]:
        """Return the current (global) operation."""
        return self._operation

    @property
    def last_error(self) -> Optional[str]:
        """Return the last message of the last error that occurred."""
        return self._last_error

    @property
    def compatible(self) -> Optional[str]:
        """Return the system compatible string."""
        return self._compatible

    @property
    def variant(self) -> Optional[str]:
        """Return the system variant string."""
        return self._variant

    @property
    def boot_slot(self) -> Optional[str]:
        """Return the used boot slot."""
        return self._boot_slot

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
    def signal_completed(self):
        """Return a signal wrapper for completed signal.

        Return a coroutine.
        """
        return self.dbus.wait_signal(f"{DBUS_NAME}.Installer.Completed")

    @dbus_connected
    async def update(self):
        """Update Properties."""
        data = await self.dbus.get_properties(f"{DBUS_NAME}.Installer")
        if not data:
            _LOGGER.warning("Can't get properties for rauc")
            return

        self._operation = data.get("Operation")
        self._last_error = data.get("LastError")
        self._compatible = data.get("Compatible")
        self._variant = data.get("Variant")
        self._boot_slot = data.get("BootSlot")
