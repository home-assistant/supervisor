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
    DBUS_ATTR_GATEWAY,
    DBUS_ATTR_ID,
    DBUS_ATTR_IP4CONFIG,
    DBUS_ATTR_IP6CONFIG,
    DBUS_ATTR_NAMESERVER_DATA,
    DBUS_ATTR_NAMESERVERS,
    DBUS_ATTR_REAL,
    DBUS_ATTR_STATE,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID,
    DBUS_NAME_DEVICE,
    DBUS_NAME_IP4CONFIG,
    DBUS_NAME_IP6CONFIG,
    DBUS_NAME_NM,
    ConnectionType,
    InterfaceMethod,
)
from .configuration import (
    EthernetProperties,
    IpConfiguration,
    NetworkAttributes,
    NetworkDevice,
    NetworkSettings,
    WirelessProperties,
)


class NetworkConnection(NetworkAttributes):
    """NetworkConnection object for Network Manager."""

    def __init__(self, object_path: str, properties: dict) -> None:
        """Initialize NetworkConnection object."""
        super().__init__(object_path, properties)
        self._device_dbus: DBus = None
        self._settings_dbus: DBus = None
        self._settings: Optional[NetworkSettings] = None
        self._ip4_config: Optional[IpConfiguration] = None
        self._ip6_config: Optional[IpConfiguration] = None
        self._device: Optional[NetworkDevice] = None
        self._wireless: Optional[WirelessProperties] = None
        self._ethernet: Optional[EthernetProperties] = None
        self.primary: bool = False

    @property
    def settings(self) -> NetworkSettings:
        """Return a settings object for the connection."""
        return self._settings

    @property
    def device(self) -> NetworkDevice:
        """Return the device used in the connection."""
        return self._device

    @property
    def default(self) -> bool:
        """Return a boolean connection is marked as default."""
        return self._properties[DBUS_ATTR_DEFAULT]

    @property
    def id(self) -> str:
        """Return the id of the connection."""
        return self._properties[DBUS_ATTR_ID]

    @property
    def type(self) -> str:
        """Return the type of the connection."""
        return self._properties[DBUS_ATTR_TYPE]

    @property
    def ip4_config(self) -> IpConfiguration:
        """Return a ip4 configuration object for the connection."""
        return self._ip4_config

    @property
    def ip6_config(self) -> IpConfiguration:
        """Return a ip6 configuration object for the connection."""
        return self._ip6_config

    @property
    def uuid(self) -> str:
        """Return the uuid of the connection."""
        return self._properties[DBUS_ATTR_UUID]

    @property
    def wireless(self) -> Optional[WirelessProperties]:
        """Return wireless properties if any."""
        if self.type != ConnectionType.WIRELESS:
            return None
        return self._wireless

    @property
    def ethernet(self) -> Optional[EthernetProperties]:
        """Return Ethernet properties if any."""
        if self.type != ConnectionType.ETHERNET:
            return None
        return self._ethernet

    @property
    def state(self) -> int:
        """
        Return the state of the connection.

        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
        """
        return self._properties[DBUS_ATTR_STATE]

    async def update_information(self):
        """Update the information for childs ."""
        settings = await DBus.connect(
            DBUS_NAME_NM, self._properties[DBUS_ATTR_CONNECTION]
        )
        device = await DBus.connect(
            DBUS_NAME_NM, self._properties[DBUS_ATTR_DEVICES][0]
        )
        ip4 = await DBus.connect(DBUS_NAME_NM, self._properties[DBUS_ATTR_IP4CONFIG])
        ip6 = await DBus.connect(DBUS_NAME_NM, self._properties[DBUS_ATTR_IP6CONFIG])

        data = (await settings.Settings.Connection.GetSettings())[0]
        device_data = await device.get_properties(DBUS_NAME_DEVICE)
        ip4_data = await ip4.get_properties(DBUS_NAME_IP4CONFIG)
        ip6_data = await ip6.get_properties(DBUS_NAME_IP6CONFIG)

        self._settings = NetworkSettings(settings)

        self._ip4_config = IpConfiguration(
            ip_address(ip4_data[DBUS_ATTR_GATEWAY])
            if DBUS_ATTR_GATEWAY in ip4_data
            else None,
            InterfaceMethod(data[ATTR_IPV4].get(ATTR_METHOD)),
            [
                ip_address(nameserver[ATTR_ADDRESS])
                for nameserver in ip4_data.get(DBUS_ATTR_NAMESERVER_DATA, [])
            ],
            [
                ip_interface(f"{address[ATTR_ADDRESS]}/{address[ATTR_PREFIX]}")
                for address in ip4_data.get(DBUS_ATTR_ADDRESS_DATA, [])
            ],
        )
        self._ip6_config = IpConfiguration(
            ip_address(ip6_data[DBUS_ATTR_GATEWAY])
            if DBUS_ATTR_GATEWAY in ip6_data
            else None,
            InterfaceMethod(data[ATTR_IPV6].get(ATTR_METHOD)),
            [
                ip_address(bytes(nameserver))
                for nameserver in ip6_data.get(DBUS_ATTR_NAMESERVERS)
            ],
            [
                ip_interface(f"{address[ATTR_ADDRESS]}/{address[ATTR_PREFIX]}")
                for address in ip6_data.get(DBUS_ATTR_ADDRESS_DATA, [])
            ],
        )

        self._wireless = WirelessProperties(
            data.get(DBUS_ATTR_802_WIRELESS, {}),
            data.get(DBUS_ATTR_802_WIRELESS_SECURITY, {}),
            bytes(data.get(DBUS_ATTR_802_WIRELESS, {}).get(ATTR_SSID, [])).decode(),
        )

        self._ethernet = EthernetProperties(data.get(DBUS_ATTR_802_ETHERNET, {}))

        self._device = NetworkDevice(
            device,
            device_data.get(DBUS_ATTR_DEVICE_INTERFACE),
            device_data.get(DBUS_ATTR_DEVICE_TYPE),
            device_data.get(DBUS_ATTR_REAL),
        )
