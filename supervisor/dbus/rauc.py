"""D-Bus interface for rauc."""
import logging

from ..exceptions import DBusError, DBusInterfaceError
from ..utils.dbus import DBus
from .const import (
    DBUS_ATTR_BOOT_SLOT,
    DBUS_ATTR_COMPATIBLE,
    DBUS_ATTR_LAST_ERROR,
    DBUS_ATTR_OPERATION,
    DBUS_ATTR_VARIANT,
    DBUS_IFACE_RAUC_INSTALLER,
    DBUS_NAME_RAUC,
    DBUS_OBJECT_BASE,
    DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED,
    RaucState,
)
from .interface import DBusInterface
from .utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Rauc(DBusInterface):
    """Handle D-Bus interface for rauc."""

    name = DBUS_NAME_RAUC

    def __init__(self):
        """Initialize Properties."""
        self._operation: str | None = None
        self._last_error: str | None = None
        self._compatible: str | None = None
        self._variant: str | None = None
        self._boot_slot: str | None = None

    async def connect(self):
        """Connect to D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_RAUC, DBUS_OBJECT_BASE)
        except DBusError:
            _LOGGER.warning("Can't connect to rauc")
        except DBusInterfaceError:
            _LOGGER.warning("Host has no rauc support. OTA updates have been disabled.")

    @property
    def operation(self) -> str | None:
        """Return the current (global) operation."""
        return self._operation

    @property
    def last_error(self) -> str | None:
        """Return the last message of the last error that occurred."""
        return self._last_error

    @property
    def compatible(self) -> str | None:
        """Return the system compatible string."""
        return self._compatible

    @property
    def variant(self) -> str | None:
        """Return the system variant string."""
        return self._variant

    @property
    def boot_slot(self) -> str | None:
        """Return the used boot slot."""
        return self._boot_slot

    @dbus_connected
    def install(self, raucb_file):
        """Install rauc bundle file.

        Return a coroutine.
        """
        return self.dbus.Installer.Install(str(raucb_file))

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
        return self.dbus.wait_signal(DBUS_SIGNAL_RAUC_INSTALLER_COMPLETED)

    @dbus_connected
    def mark(self, state: RaucState, slot_identifier: str):
        """Get slot status.

        Return a coroutine.
        """
        return self.dbus.Installer.Mark(state, slot_identifier)

    @dbus_connected
    async def update(self):
        """Update Properties."""
        data = await self.dbus.get_properties(DBUS_IFACE_RAUC_INSTALLER)
        if not data:
            _LOGGER.warning("Can't get properties for rauc")
            return

        self._operation = data.get(DBUS_ATTR_OPERATION)
        self._last_error = data.get(DBUS_ATTR_LAST_ERROR)
        self._compatible = data.get(DBUS_ATTR_COMPATIBLE)
        self._variant = data.get(DBUS_ATTR_VARIANT)
        self._boot_slot = data.get(DBUS_ATTR_BOOT_SLOT)
