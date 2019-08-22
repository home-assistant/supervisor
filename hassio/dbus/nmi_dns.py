"""D-Bus interface for hostname."""
import logging

from .interface import DBusInterface
from .utils import dbus_connected
from ..exceptions import DBusError, DBusInterfaceError
from ..utils.gdbus import DBus

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_NAME = "org.freedesktop.NetworkManager"
DBUS_OBJECT = "/org/freedesktop/NetworkManager/DnsManager"


class NMIDnsManager(DBusInterface):
    """Handle D-Bus interface for NMI DnsManager."""

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME, DBUS_OBJECT)
        except DBusError:
            _LOGGER.warning("Can't connect to DnsManager")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No DnsManager support on the host. Local DNS functions have been disabled."
            )

    @dbus_connected
    def get_properties(self):
        """Return local host informations.

        Return a coroutine.
        """
        return self.dbus.get_properties(f"{DBUS_NAME}.DnsManager")
