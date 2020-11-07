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

        self._settings_dbus: DBus = None
        self._settings: Optional[NetworkSettings] = None
        self._ip4_config: Optional[IpConfiguration] = None
        self._ip6_config: Optional[IpConfiguration] = None
        self._wireless: Optional[WirelessProperties] = None
        self._ethernet: Optional[EthernetProperties] = None

    @property
    def settings(self) -> NetworkSettings:
        """Return a settings object for the connection."""
        return self._settings

    @property
    def default(self) -> bool:
        """Return a boolean connection is marked as default."""
        return self.properties[DBUS_ATTR_DEFAULT]

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
    def ip4_config(self) -> Optional[IpConfiguration]:
        """Return a ip4 configuration object for the connection."""
        return self._ip4_config

    @property
    def ip6_config(self) -> Optional[IpConfiguration]:
        """Return a ip6 configuration object for the connection."""
        return self._ip6_config

    @property
    def wireless(self) -> Optional[WirelessProperties]:
        """Return wireless properties if any."""
        return self._wireless

    @property
    def ethernet(self) -> Optional[EthernetProperties]:
        """Return Ethernet properties if any."""
        return self._ethernet

    @property
    def state(self) -> int:
        """
        Return the state of the connection.

        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
        """
        return self._properties[DBUS_ATTR_STATE]

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        self.properties = await self.dbus.get_properties(DBUS_NAME_CONNECTION_ACTIVE)

        data = (await settings.Settings.Connection.GetSettings())[0]

        self._settings = NetworkSettings(settings)

        if self.type == ConnectionType.WIRELESS:
            wifi = await DBus.connect(
                DBUS_NAME_DEVICE_WIRELESS, self._properties[DBUS_ATTR_DEVICES][0]
            )
            self._wireless = WirelessProperties(
                wifi,
                data.get(DBUS_ATTR_802_WIRELESS, {}),
                data.get(DBUS_ATTR_802_WIRELESS_SECURITY, {}),
                bytes(data.get(DBUS_ATTR_802_WIRELESS, {}).get(ATTR_SSID, [])).decode(),
            )

        if self.type == ConnectionType.ETHERNET:
            self._ethernet = EthernetProperties(data.get(DBUS_ATTR_802_ETHERNET, {}))
