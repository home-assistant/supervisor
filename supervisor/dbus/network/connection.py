"""Connection object for Network Manager."""
from ipaddress import ip_address, ip_interface
from typing import Optional

from ...const import (
    ATTR_ADDRESS,
    ATTR_IPV4,
    ATTR_IPV6,
    ATTR_METHOD,
    ATTR_PREFIX,
    ATTR_SSID,
)
from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_802_ETHERNET,
    DBUS_ATTR_802_WIRELESS,
    DBUS_ATTR_802_WIRELESS_SECURITY,
    DBUS_ATTR_ADDRESS_DATA,
    DBUS_ATTR_CONNECTION,
    DBUS_ATTR_DEFAULT,
    DBUS_ATTR_DEVICE_INTERFACE,
    DBUS_ATTR_DEVICE_TYPE,
    DBUS_ATTR_DEVICES,
    DBUS_ATTR_DRIVER,
    DBUS_ATTR_GATEWAY,
    DBUS_ATTR_ID,
    DBUS_ATTR_IP4CONFIG,
    DBUS_ATTR_IP6CONFIG,
    DBUS_ATTR_NAMESERVER_DATA,
    DBUS_ATTR_NAMESERVERS,
    DBUS_ATTR_STATE,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID,
    DBUS_NAME_CONNECTION_ACTIVE,
    DBUS_NAME_DEVICE,
    DBUS_NAME_DEVICE_WIRELESS,
    DBUS_NAME_IP4CONFIG,
    DBUS_NAME_IP6CONFIG,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    ConnectionType,
    InterfaceMethod,
)
from ..interface import DBusInterfaceProxy
from .configuration import (
    EthernetProperties,
    IpConfiguration,
    NetworkDevice,
    NetworkSettings,
    WirelessProperties,
)


class NetworkConnection(DBusInterfaceProxy):
    """NetworkConnection object for Network Manager."""

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
    def state(self) -> int:
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
        self.properties = await self.dbus.get_properties(DBUS_NAME_CONNECTION_ACTIVE)

        # IPv4
        if self.properties[DBUS_ATTR_IP4CONFIG] != DBUS_OBJECT_BASE:
            ip4 = await DBus.connect(DBUS_NAME_NM, self.properties[DBUS_ATTR_IP4CONFIG])
            ip4_data = await ip4.get_properties(DBUS_NAME_IP4CONFIG)

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
            ip6_data = await ip6.get_properties(DBUS_NAME_IP6CONFIG)

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
