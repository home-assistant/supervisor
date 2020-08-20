"""Connection object for Network Manager."""
import logging
from typing import Optional

from ...utils.gdbus import DBus
from .configuration import (
    AddressData,
    IpConfiguration,
    NetworkAttributes,
    NetworkDevice,
    NetworkSettings,
)
from .const import (
    ATTR_ADDRESS,
    ATTR_CONNECTION,
    ATTR_DEFAULT,
    ATTR_DEVICE_INTERFACE,
    ATTR_DEVICE_TYPE,
    ATTR_DEVICES,
    ATTR_ID,
    ATTR_IP4ADDRESS,
    ATTR_PREFIX,
    ATTR_REAL,
    ATTR_STATE,
    ATTR_TYPE,
    ATTR_UUID,
    DBUS_NAME_DEVICE,
    DBUS_NAME_NM,
)

_LOGGER = logging.getLogger(__name__)


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
        return self._properties[ATTR_DEFAULT]

    @property
    def id(self) -> str:
        """Return the id of the connection."""
        return self._properties[ATTR_ID]

    @property
    def type(self) -> str:
        """Return the type of the connection."""
        return self._properties[ATTR_TYPE]

    @property
    def ip4_config(self) -> IpConfiguration:
        """Return a ip configuration object for the connection."""
        return self._ip4_config

    @property
    def uuid(self) -> str:
        """Return the uuid of the connection."""
        return self._properties[ATTR_UUID]

    @property
    def state(self) -> int:
        """
        Return the state of the connection.

        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
        """
        return self._properties[ATTR_STATE]

    async def update_information(self):
        """Update the information for childs ."""
        settings = await DBus.connect(DBUS_NAME_NM, self._properties[ATTR_CONNECTION])
        device = await DBus.connect(DBUS_NAME_NM, self._properties[ATTR_DEVICES][0])

        data = await settings.Settings.Connection.GetSettings()
        data = data.pop()
        device_data = await device.get_properties(DBUS_NAME_DEVICE)

        self._settings = NetworkSettings(settings)

        self._ip4_config = IpConfiguration(
            data["ipv4"].get("gateway"),
            data["ipv4"].get("method"),
            data["ipv4"].get("dns"),
            AddressData(
                data["ipv4"].get("address-data")[0].get(ATTR_ADDRESS),
                data["ipv4"].get("address-data")[0].get(ATTR_PREFIX),
            ),
        )

        self._device = NetworkDevice(
            device,
            device_data.get(ATTR_DEVICE_INTERFACE),
            device_data.get(ATTR_IP4ADDRESS),
            device_data.get(ATTR_DEVICE_TYPE),
            device_data.get(ATTR_REAL),
        )
