"""Connection object for Network Manager."""
import logging
from typing import Any, Awaitable, Optional

from ....const import ATTR_METHOD, ATTR_MODE, ATTR_PSK, ATTR_SSID
from ....utils.dbus import DBus
from ...const import DBUS_NAME_NM
from ...interface import DBusInterfaceProxy
from ...utils import dbus_connected
from ..configuration import (
    ConnectionProperties,
    EthernetProperties,
    IpProperties,
    VlanProperties,
    WirelessProperties,
    WirelessSecurityProperties,
)

CONF_ATTR_CONNECTION = "connection"
CONF_ATTR_802_ETHERNET = "802-3-ethernet"
CONF_ATTR_802_WIRELESS = "802-11-wireless"
CONF_ATTR_802_WIRELESS_SECURITY = "802-11-wireless-security"
CONF_ATTR_VLAN = "vlan"
CONF_ATTR_IPV4 = "ipv4"
CONF_ATTR_IPV6 = "ipv6"

ATTR_ID = "id"
ATTR_UUID = "uuid"
ATTR_TYPE = "type"
ATTR_PARENT = "parent"
ATTR_ASSIGNED_MAC = "assigned-mac-address"
ATTR_POWERSAVE = "powersave"
ATTR_AUTH_ALG = "auth-alg"
ATTR_KEY_MGMT = "key-mgmt"
ATTR_INTERFACE_NAME = "interface-name"

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkSetting(DBusInterfaceProxy):
    """Network connection setting object for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Settings.Connection.html
    """

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self._connection: Optional[ConnectionProperties] = None
        self._wireless: Optional[WirelessProperties] = None
        self._wireless_security: Optional[WirelessSecurityProperties] = None
        self._ethernet: Optional[EthernetProperties] = None
        self._vlan: Optional[VlanProperties] = None
        self._ipv4: Optional[IpProperties] = None
        self._ipv6: Optional[IpProperties] = None

    @property
    def connection(self) -> Optional[ConnectionProperties]:
        """Return connection properties if any."""
        return self._connection

    @property
    def wireless(self) -> Optional[WirelessProperties]:
        """Return wireless properties if any."""
        return self._wireless

    @property
    def wireless_security(self) -> Optional[WirelessSecurityProperties]:
        """Return wireless security properties if any."""
        return self._wireless_security

    @property
    def ethernet(self) -> Optional[EthernetProperties]:
        """Return Ethernet properties if any."""
        return self._ethernet

    @property
    def vlan(self) -> Optional[VlanProperties]:
        """Return Vlan properties if any."""
        return self._vlan

    @property
    def ipv4(self) -> Optional[IpProperties]:
        """Return ipv4 properties if any."""
        return self._ipv4

    @property
    def ipv6(self) -> Optional[IpProperties]:
        """Return ipv6 properties if any."""
        return self._ipv6

    @dbus_connected
    def get_settings(self) -> Awaitable[Any]:
        """Return connection settings."""
        return self.dbus.Settings.Connection.GetSettings()

    @dbus_connected
    def update(self, settings: Any) -> Awaitable[None]:
        """Update connection settings."""
        return self.dbus.Settings.Connection.Update(("a{sa{sv}}", settings))

    @dbus_connected
    def delete(self) -> Awaitable[None]:
        """Delete connection settings."""
        return self.dbus.Settings.Connection.Delete()

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        data = (await self.get_settings())[0]

        # Get configuration settings we care about
        # See: https://developer-old.gnome.org/NetworkManager/stable/ch01.html
        if CONF_ATTR_CONNECTION in data:
            self._connection = ConnectionProperties(
                data[CONF_ATTR_CONNECTION].get(ATTR_ID),
                data[CONF_ATTR_CONNECTION].get(ATTR_UUID),
                data[CONF_ATTR_CONNECTION].get(ATTR_TYPE),
                data[CONF_ATTR_CONNECTION].get(ATTR_INTERFACE_NAME),
            )

        if CONF_ATTR_802_ETHERNET in data:
            self._ethernet = EthernetProperties(
                data[CONF_ATTR_802_ETHERNET].get(ATTR_ASSIGNED_MAC),
            )

        if CONF_ATTR_802_WIRELESS in data:
            self._wireless = WirelessProperties(
                bytes(data[CONF_ATTR_802_WIRELESS].get(ATTR_SSID, [])).decode(),
                data[CONF_ATTR_802_WIRELESS].get(ATTR_ASSIGNED_MAC),
                data[CONF_ATTR_802_WIRELESS].get(ATTR_MODE),
                data[CONF_ATTR_802_WIRELESS].get(ATTR_POWERSAVE),
            )

        if CONF_ATTR_802_WIRELESS_SECURITY in data:
            self._wireless_security = WirelessSecurityProperties(
                data[CONF_ATTR_802_WIRELESS_SECURITY].get(ATTR_AUTH_ALG),
                data[CONF_ATTR_802_WIRELESS_SECURITY].get(ATTR_KEY_MGMT),
                data[CONF_ATTR_802_WIRELESS_SECURITY].get(ATTR_PSK),
            )

        if CONF_ATTR_VLAN in data:
            self._vlan = VlanProperties(
                data[CONF_ATTR_VLAN].get(ATTR_ID),
                data[CONF_ATTR_VLAN].get(ATTR_PARENT),
            )

        if CONF_ATTR_IPV4 in data:
            self._ipv4 = IpProperties(
                data[CONF_ATTR_IPV4].get(ATTR_METHOD),
            )

        if CONF_ATTR_IPV6 in data:
            self._ipv6 = IpProperties(
                data[CONF_ATTR_IPV6].get(ATTR_METHOD),
            )
