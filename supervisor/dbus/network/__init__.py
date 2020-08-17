"""Network Manager implementation for DBUS."""
import logging
from typing import List, Optional

from ...exceptions import DBusError, DBusInterfaceError
from ...utils.gdbus import DBus
from ..interface import DBusInterface
from ..utils import dbus_connected
from .connection import NetworkConnection
from .const import DBUS_NAME_NM, DBUS_OBJECT_NM

_LOGGER = logging.getLogger(__name__)


class NetworkManager(DBusInterface):
    """Handle D-Bus interface for Network Manager."""

    def __init__(self) -> None:
        """Initialize Properties."""
        self._primary_connection: Optional[NetworkConnection] = None
        self._connections: Optional[List[NetworkConnection]] = None

    @property
    def primary_connection(self) -> NetworkConnection:
        """Return the primary connection."""
        return self._primary_connection

    @property
    def connections(self) -> List[NetworkConnection]:
        """Return a list of active connections."""
        return self._connections

    async def connect(self) -> None:
        """Connect to system's D-Bus."""
        try:
            self.dbus = await DBus.connect(DBUS_NAME_NM, DBUS_OBJECT_NM)
        except DBusError:
            _LOGGER.warning("Can't connect to Network Manager")
        except DBusInterfaceError:
            _LOGGER.warning(
                "No Network Manager support on the host. Local network functions have been disabled."
            )

    @dbus_connected
    async def update(self):
        """Update Properties."""
        data = await self.dbus.get_properties(DBUS_NAME_NM)
        if not data:
            _LOGGER.warning("Can't get properties for Network Manager")
            return
        _LOGGER.debug(data)
        self._connections = []
        for active_connection in data.get("ActiveConnections", []):
            connection: NetworkConnection = await self.get_connection(active_connection)
            if not connection.default:
                continue
            await connection.update_information()
            if connection.object_path == data.get("PrimaryConnection"):
                self._primary_connection = connection
            self._connections.append(connection)

    @dbus_connected
    async def get_connection(self, connection_object: str) -> NetworkConnection:
        """Get connection information."""
        connection = await self.dbus.connect(DBUS_NAME_NM, connection_object)
        connection_properties = await connection.get_properties(
            f"{DBUS_NAME_NM}.Connection.Active"
        )
        return NetworkConnection(connection_object, connection_properties)
