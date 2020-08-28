"""NetworkInterface object for Network Manager."""
from ...utils.gdbus import DBus
from ..const import (
    DBUS_NAME_CONNECTION_ACTIVE,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    InterfaceMethod,
)
from ..payloads.generate import interface_update_payload
from .connection import NetworkConnection


class NetworkInterface:
    """NetworkInterface object for Network Manager, this serves as a proxy to other objects."""

    def __init__(self) -> None:
        """Initialize NetworkConnection object."""
        self._connection = None
        self._nm_dbus = None

    @property
    def nm_dbus(self) -> DBus:
        """Return the NM DBus connection."""
        return self._nm_dbus

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
    def prefix(self) -> str:
        """Return the network prefix."""
        return self.connection.ip4_config.address_data.prefix

    @property
    def type(self) -> str:
        """Return the interface type."""
        return self.connection.type

    @property
    def id(self) -> str:
        """Return the interface id."""
        return self.connection.id

    @property
    def method(self) -> InterfaceMethod:
        """Return the interface method."""
        return InterfaceMethod(self.connection.ip4_config.method)

    @property
    def gateway(self) -> str:
        """Return the gateway."""
        return self.connection.ip4_config.gateway

    @property
    def nameservers(self) -> str:
        """Return the nameservers."""
        return self.connection.ip4_config.nameservers

    async def connect(self, nm_dbus: DBus, connection_object: str) -> None:
        """Get connection information."""
        self._nm_dbus = nm_dbus
        connection_bus = await DBus.connect(DBUS_NAME_NM, connection_object)
        connection_properties = await connection_bus.get_properties(
            DBUS_NAME_CONNECTION_ACTIVE
        )
        self._connection = NetworkConnection(connection_object, connection_properties)

    async def update_settings(self, **kwargs) -> None:
        """Update IP configuration used for this interface."""
        payload = interface_update_payload(self, **kwargs)

        await self.connection.settings.dbus.Settings.Connection.Update(payload)

        await self.nm_dbus.ActivateConnection(
            self.connection.settings.dbus.object_path,
            self.connection.device.dbus.object_path,
            DBUS_OBJECT_BASE,
        )
