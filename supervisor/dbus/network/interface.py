"""NetworkInterface object for Network Manager."""
from supervisor.exceptions import APIError

from ...const import ATTR_ADDRESS, ATTR_DNS, ATTR_GATEWAY, ATTR_METHOD, ATTR_PREFIX
from ...utils.gdbus import DBus
from ..const import (
    DBUS_NAME_CONNECTION_ACTIVE,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    InterfaceMethod,
)
from .connection import NetworkConnection
from .utils import ip2int


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
        if kwargs.get(ATTR_DNS):
            if not isinstance(kwargs[ATTR_DNS], list):
                raise APIError("DNS addresses is not a list!")
            kwargs[ATTR_DNS] = [ip2int(x.strip()) for x in kwargs[ATTR_DNS]]

        if kwargs.get(ATTR_METHOD):
            kwargs[ATTR_METHOD] = (
                InterfaceMethod.MANUAL
                if kwargs[ATTR_METHOD] == "static"
                else InterfaceMethod.AUTO
            )

        if kwargs.get(ATTR_ADDRESS):
            if "/" in kwargs[ATTR_ADDRESS]:
                kwargs[ATTR_PREFIX] = kwargs[ATTR_ADDRESS].split("/")[-1]
                kwargs[ATTR_ADDRESS] = kwargs[ATTR_ADDRESS].split("/")[0]
                kwargs[ATTR_METHOD] = InterfaceMethod.MANUAL

        await self.connection.settings.dbus.Settings.Connection.Update(
            f"""{{
                    'connection':
                        {{
                            'id': <'{self.id}'>,
                            'type': <'{self.type}'>
                        }},
                    'ipv4':
                        {{
                            'method': <'{kwargs.get(ATTR_METHOD, self.method)}'>,
                            'dns': <[{",".join([f"uint32 {x}" for x in kwargs.get(ATTR_DNS, self.nameservers)])}]>,
                            'address-data': <[
                                {{
                                    'address': <'{kwargs.get(ATTR_ADDRESS, self.ip_address)}'>,
                                    'prefix': <uint32 {kwargs.get(ATTR_PREFIX, self.prefix)}>
                                }}]>,
                            'gateway': <'{kwargs.get(ATTR_GATEWAY, self.gateway)}'>
                                }}
                }}"""
        )

        await self.nm_dbus.ActivateConnection(
            self.connection.settings.dbus.object_path,
            self.connection.device.dbus.object_path,
            DBUS_OBJECT_BASE,
        )
