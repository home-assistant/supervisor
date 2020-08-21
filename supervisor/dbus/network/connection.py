"""Connection object for Network Manager."""
from typing import Optional

from ...const import (
    ATTR_ADDRESS,
    ATTR_ADDRESS_DATA,
    ATTR_DNS,
    ATTR_GATEWAY,
    ATTR_IPV4,
    ATTR_METHOD,
    ATTR_PREFIX,
)
from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_CONNECTION,
    DBUS_ATTR_DEFAULT,
    DBUS_ATTR_DEVICE_INTERFACE,
    DBUS_ATTR_DEVICE_TYPE,
    DBUS_ATTR_DEVICES,
    DBUS_ATTR_ID,
    DBUS_ATTR_IP4ADDRESS,
    DBUS_ATTR_REAL,
    DBUS_ATTR_STATE,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID,
    DBUS_NAME_DEVICE,
    DBUS_NAME_NM,
)
from .configuration import (
    AddressData,
    IpConfiguration,
    NetworkAttributes,
    NetworkDevice,
    NetworkSettings,
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

        data = await settings.Settings.Connection.GetSettings()
        data = data.pop()
        device_data = await device.get_properties(DBUS_NAME_DEVICE)

        self._settings = NetworkSettings(settings)

        self._ip4_config = IpConfiguration(
            data[ATTR_IPV4].get(ATTR_GATEWAY),
            data[ATTR_IPV4].get(ATTR_METHOD),
            data[ATTR_IPV4].get(ATTR_DNS),
            AddressData(
                data[ATTR_IPV4].get(ATTR_ADDRESS_DATA)[0].get(ATTR_ADDRESS),
                data[ATTR_IPV4].get(ATTR_ADDRESS_DATA)[0].get(ATTR_PREFIX),
            ),
        )

        self._device = NetworkDevice(
            device,
            device_data.get(DBUS_ATTR_DEVICE_INTERFACE),
            device_data.get(DBUS_ATTR_IP4ADDRESS),
            device_data.get(DBUS_ATTR_DEVICE_TYPE),
            device_data.get(DBUS_ATTR_REAL),
        )
