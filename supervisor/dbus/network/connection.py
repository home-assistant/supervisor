"""Connection object for Network Manager."""
from typing import Optional

from ...const import ATTR_ADDRESS, ATTR_IPV4, ATTR_METHOD, ATTR_PREFIX
from ...utils.gdbus import DBus
from ..const import (
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
    DBUS_ATTR_IP4ADDRESS,
    DBUS_ATTR_IP4CONFIG,
    DBUS_ATTR_NAMESERVERS,
    DBUS_ATTR_REAL,
    DBUS_ATTR_STATE,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID,
    DBUS_NAME_DEVICE,
    DBUS_NAME_IP4CONFIG,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    ConnectionType,
)
from .configuration import (
    AddressData,
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
        self._device: Optional[NetworkDevice]
        self._wireless: Optional[WirelessProperties] = None
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
        """Return a ip configuration object for the connection."""
        return self._ip4_config

    @property
    def uuid(self) -> str:
        """Return the uuid of the connection."""
        return self._properties[DBUS_ATTR_UUID]

    @property
    def wireless(self) -> str:
        """Return wireless properties if any."""
        if self.type != ConnectionType.WIRELESS:
            return None
        return self._wireless

    @property
    def state(self) -> int:
        """
        Return the state of the connection.

        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
        """
        return self._properties[DBUS_ATTR_STATE]

    async def update_information(self):
        """Update the information for childs ."""
        if self._properties[DBUS_ATTR_IP4CONFIG] == DBUS_OBJECT_BASE:
            return

        settings = await DBus.connect(
            DBUS_NAME_NM, self._properties[DBUS_ATTR_CONNECTION]
        )
        device = await DBus.connect(
            DBUS_NAME_NM, self._properties[DBUS_ATTR_DEVICES][0]
        )
        ip4 = await DBus.connect(DBUS_NAME_NM, self._properties[DBUS_ATTR_IP4CONFIG])

        data = (await settings.Settings.Connection.GetSettings())[0]
        device_data = await device.get_properties(DBUS_NAME_DEVICE)
        ip4_data = await ip4.get_properties(DBUS_NAME_IP4CONFIG)

        self._settings = NetworkSettings(settings)

        self._ip4_config = IpConfiguration(
            ip4_data.get(DBUS_ATTR_GATEWAY),
            data[ATTR_IPV4].get(ATTR_METHOD),
            ip4_data.get(DBUS_ATTR_NAMESERVERS),
            AddressData(
                ip4_data.get(DBUS_ATTR_ADDRESS_DATA)[0].get(ATTR_ADDRESS),
                ip4_data.get(DBUS_ATTR_ADDRESS_DATA)[0].get(ATTR_PREFIX),
            ),
        )

        self._wireless = WirelessProperties(
            data.get(DBUS_ATTR_802_WIRELESS, {}),
            data.get(DBUS_ATTR_802_WIRELESS_SECURITY, {}),
        )

        self._device = NetworkDevice(
            device,
            device_data.get(DBUS_ATTR_DEVICE_INTERFACE),
            device_data.get(DBUS_ATTR_IP4ADDRESS),
            device_data.get(DBUS_ATTR_DEVICE_TYPE),
            device_data.get(DBUS_ATTR_REAL),
        )
