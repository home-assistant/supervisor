"""NetworkInterface object for Network Manager."""
from typing import Optional

from ...utils.gdbus import DBus
from ..const import DBUS_NAME_CONNECTION_ACTIVE, DBUS_NAME_NM, DBUS_OBJECT_BASE
from ..payloads.generate import interface_update_payload
from .connection import NetworkConnection


class NetworkInterface:
    """NetworkInterface object for Network Manager, this serves as a proxy to other objects."""

    def __init__(self, dbus: DBus) -> None:
        """Initialize NetworkConnection object."""
        self._connection: Optional[NetworkConnection] = None
        self._nm_dbus: DBus = dbus

    @property
    def connection(self) -> NetworkConnection:
        """Return the connection used for this interface."""
        if self._connection is None:
            raise RuntimeError()
        return self._connection

    async def connect(self, connection_object: str) -> None:
        """Get connection information."""
        connection_bus = await DBus.connect(DBUS_NAME_NM, connection_object)
        connection_properties = await connection_bus.get_properties(
            DBUS_NAME_CONNECTION_ACTIVE
        )
        self._connection = NetworkConnection(connection_object, connection_properties)

    async def update_settings(self, interface_data: dict) -> None:
        """Update IP configuration used for this interface."""
        payload = interface_update_payload(interface_data)

        await self.connection.settings.dbus.Settings.Connection.Update(payload)

        await self._nm_dbus.ActivateConnection(
            self.connection.settings.dbus.object_path,
            self.connection.device.dbus.object_path,
            DBUS_OBJECT_BASE,
        )
