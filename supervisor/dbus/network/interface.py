"""NetworkInterface object for Network Manager."""
from ...utils.gdbus import DBus
from .connection import NetworkConnection
from .const import DBUS_NAME_CONNECTION_ACTIVE, DBUS_NAME_NM


class NetworkInterface:
    """NetworkInterface object for Network Manager, this serves as a proxy to other objects."""

    def __init__(self) -> None:
        """Initialize NetworkConnection object."""
        self._connection = None

    @property
    def connection(self) -> NetworkConnection:
        """Return the connection used for this interface."""
        return self._connection

    @property
    def name(self) -> str:
        """Return the interface name."""
        return self.connection.device.interface

    @property
    def primary(self) -> bool:
        """Return true if it's the primary interfac."""
        return self.connection.primary

    @property
    def ip_address(self) -> str:
        """Return the ip_address."""
        return self.connection.ip4_config.address_data.address

    @property
    def type(self) -> str:
        """Return the interface type."""
        return self.connection.type

    @property
    def id(self) -> str:
        """Return the interface id."""
        return self.connection.id

    @property
    def gateway(self) -> str:
        """Return the gateway."""
        return self.connection.ip4_config.gateway

    async def connect(self, connection_object: str) -> None:
        """Get connection information."""
        connection_bus = await DBus.connect(DBUS_NAME_NM, connection_object)
        connection_properties = await connection_bus.get_properties(
            DBUS_NAME_CONNECTION_ACTIVE
        )
        self._connection = NetworkConnection(connection_object, connection_properties)
