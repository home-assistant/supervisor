"""Network Manager implementation for DBUS."""
import logging
from typing import Any, Awaitable

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.dbus_next import DBus
from ..const import DBUS_NAME_NM, DBUS_OBJECT_SETTINGS
from ..interface import DBusInterface
from ..utils import dbus_connected

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkManagerSettings(DBusInterface):
    """Handle D-Bus interface for Network Manager."""

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_NM, DBUS_OBJECT_SETTINGS)
        except DBusError:
            _LOGGER.warning("Can't connect to Network Manager Settings")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No Network Manager Settings support on the host. Local network functions have been disabled."
            )

    @dbus_connected
    def add_connection(self, settings: Any) -> Awaitable[Any]:
        """Add new connection."""
        return self.dbus.Settings.AddConnection(("a{sa{sv}}", settings))

    @dbus_connected
    def reload_connections(self) -> Awaitable[Any]:
        """Reload all local connection files."""
        return self.dbus.Settings.ReloadConnections()
