"""IP Configuration object for Network Manager."""

from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv6Address,
    IPv6Interface,
    ip_address,
    ip_interface,
)

from ...const import ATTR_ADDRESS, ATTR_PREFIX
from ..const import (
    DBUS_ATTR_ADDRESS_DATA,
    DBUS_ATTR_GATEWAY,
    DBUS_ATTR_NAMESERVER_DATA,
    DBUS_ATTR_NAMESERVERS,
    DBUS_IFACE_IP4CONFIG,
    DBUS_IFACE_IP6CONFIG,
    DBUS_NAME_NM,
)
from ..interface import DBusInterfaceProxy, dbus_property


class IpConfiguration(DBusInterfaceProxy):
    """IP Configuration object for Network Manager."""

    bus_name: str = DBUS_NAME_NM

    def __init__(self, object_path: str, ip4: bool = True) -> None:
        """Initialize properties."""
        self._ip4: bool = ip4
        self._object_path: str = object_path
        self._properties_interface: str = (
            DBUS_IFACE_IP4CONFIG if ip4 else DBUS_IFACE_IP6CONFIG
        )
        super().__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    def properties_interface(self) -> str:
        """Primary interface of object to get property values from."""
        return self._properties_interface

    @property
    @dbus_property
    def gateway(self) -> IPv4Address | IPv6Address | None:
        """Get gateway."""
        return (
            ip_address(self.properties[DBUS_ATTR_GATEWAY])
            if self.properties.get(DBUS_ATTR_GATEWAY)
            else None
        )

    @property
    @dbus_property
    def nameservers(self) -> list[IPv4Address | IPv6Address]:
        """Get nameservers."""
        if self._ip4:
            return [
                ip_address(nameserver[ATTR_ADDRESS])
                for nameserver in self.properties[DBUS_ATTR_NAMESERVER_DATA]
            ]

        return [
            ip_address(bytes(nameserver))
            for nameserver in self.properties[DBUS_ATTR_NAMESERVERS]
        ]

    @property
    @dbus_property
    def address(self) -> list[IPv4Interface | IPv6Interface]:
        """Get address."""
        return [
            ip_interface(f"{address[ATTR_ADDRESS]}/{address[ATTR_PREFIX]}")
            for address in self.properties[DBUS_ATTR_ADDRESS_DATA]
        ]
