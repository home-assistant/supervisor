"""Connection object for Network Manager."""
from ipaddress import ip_address, ip_interface
from typing import Optional

from supervisor.dbus.utils import dbus_connected

from ...const import ATTR_ADDRESS, ATTR_PREFIX
from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_ADDRESS_DATA,
    DBUS_ATTR_CONNECTION,
    DBUS_ATTR_GATEWAY,
    DBUS_ATTR_ID,
    DBUS_ATTR_IP4CONFIG,
    DBUS_ATTR_IP6CONFIG,
    DBUS_ATTR_NAMESERVER_DATA,
    DBUS_ATTR_NAMESERVERS,
    DBUS_ATTR_STATE,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID,
    DBUS_IFACE_CONNECTION_ACTIVE,
    DBUS_IFACE_IP4CONFIG,
    DBUS_IFACE_IP6CONFIG,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    ConnectionStateType,
)
from ..interface import DBusInterfaceProxy
from .configuration import IpConfiguration


class NetworkConnection(DBusInterfaceProxy):
    """Active network connection object for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Connection.Active.html
    """

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self._ipv4: Optional[IpConfiguration] = None
        self._ipv6: Optional[IpConfiguration] = None

    @property
    def id(self) -> str:
        """Return the id of the connection."""
        return self.properties[DBUS_ATTR_ID]

    @property
    def type(self) -> str:
        """Return the type of the connection."""
        return self.properties[DBUS_ATTR_TYPE]

    @property
    def uuid(self) -> str:
        """Return the uuid of the connection."""
        return self.properties[DBUS_ATTR_UUID]

    @property
    def state(self) -> ConnectionStateType:
        """Return the state of the connection."""
        return self.properties[DBUS_ATTR_STATE]

    @property
    def setting_object(self) -> int:
        """Return the connection object path."""
        return self.properties[DBUS_ATTR_CONNECTION]

    @property
    def ipv4(self) -> Optional[IpConfiguration]:
        """Return a ip4 configuration object for the connection."""
        return self._ipv4

    @property
    def ipv6(self) -> Optional[IpConfiguration]:
        """Return a ip6 configuration object for the connection."""
        return self._ipv6

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        await self.update()

    @dbus_connected
    async def update(self):
        """Update connection information."""
        self.properties = await self.dbus.get_properties(DBUS_IFACE_CONNECTION_ACTIVE)

        # IPv4
        if self.properties[DBUS_ATTR_IP4CONFIG] != DBUS_OBJECT_BASE:
            ip4 = await DBus.connect(DBUS_NAME_NM, self.properties[DBUS_ATTR_IP4CONFIG])
            ip4_data = await ip4.get_properties(DBUS_IFACE_IP4CONFIG)

            self._ipv4 = IpConfiguration(
                ip_address(ip4_data[DBUS_ATTR_GATEWAY])
                if ip4_data.get(DBUS_ATTR_GATEWAY)
                else None,
                [
                    ip_address(nameserver[ATTR_ADDRESS])
                    for nameserver in ip4_data.get(DBUS_ATTR_NAMESERVER_DATA, [])
                ],
                [
                    ip_interface(f"{address[ATTR_ADDRESS]}/{address[ATTR_PREFIX]}")
                    for address in ip4_data.get(DBUS_ATTR_ADDRESS_DATA, [])
                ],
            )

        # IPv6
        if self.properties[DBUS_ATTR_IP6CONFIG] != DBUS_OBJECT_BASE:
            ip6 = await DBus.connect(DBUS_NAME_NM, self.properties[DBUS_ATTR_IP6CONFIG])
            ip6_data = await ip6.get_properties(DBUS_IFACE_IP6CONFIG)

            self._ipv6 = IpConfiguration(
                ip_address(ip6_data[DBUS_ATTR_GATEWAY])
                if ip6_data.get(DBUS_ATTR_GATEWAY)
                else None,
                [
                    ip_address(bytes(nameserver))
                    for nameserver in ip6_data.get(DBUS_ATTR_NAMESERVERS)
                ],
                [
                    ip_interface(f"{address[ATTR_ADDRESS]}/{address[ATTR_PREFIX]}")
                    for address in ip6_data.get(DBUS_ATTR_ADDRESS_DATA, [])
                ],
            )
