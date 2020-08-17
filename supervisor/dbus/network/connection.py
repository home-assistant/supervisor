"""Connection object for Network Manager."""
import logging
from typing import Optional

from ...utils.gdbus import DBus
from .configuration import (
    AddressData,
    IpConfiguration,
    NetworkAttributes,
    NetworkSettings,
)
from .const import (
    ATTR_ADDRESS,
    ATTR_ADDRESS_DATA,
    ATTR_CONNECTION,
    ATTR_DEFAULT,
    ATTR_FILENAME,
    ATTR_FLAGS,
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_IP4CONFIG,
    ATTR_PREFIX,
    ATTR_STATE,
    ATTR_TYPE,
    ATTR_UNSAVED,
    ATTR_UUID,
    DBUS_NAME_IP4CONFIG,
    DBUS_NAME_NM,
    DBUS_NAME_SETTINGS_CONNECTION,
)

_LOGGER = logging.getLogger(__name__)


class NetworkConnection(NetworkAttributes):
    """NetworkConnection object for Network Manager."""

    def __init__(self, object_path: str, properties: dict) -> None:
        """Initialize NetworkConnection object."""
        super().__init__(object_path, properties)
        self._settings: Optional[NetworkSettings] = None
        self._ip4_config: Optional[IpConfiguration] = None

    @property
    def settings(self) -> NetworkSettings:
        """Return a settings object for the connection."""
        return self._settings

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
        connection_path = self._properties[ATTR_CONNECTION]
        ip4config_path = self._properties[ATTR_IP4CONFIG]

        settings = await DBus.connect(DBUS_NAME_NM, connection_path)
        ip4_config = await DBus.connect(DBUS_NAME_NM, ip4config_path)

        settings_data = await settings.get_properties(DBUS_NAME_SETTINGS_CONNECTION)
        ip4_config_data = await ip4_config.get_properties(DBUS_NAME_IP4CONFIG)

        self._settings = NetworkSettings(
            settings_data.get(ATTR_FLAGS),
            settings_data.get(ATTR_UNSAVED),
            settings_data.get(ATTR_FILENAME),
        )
        self._ip4_config = IpConfiguration(
            ip4_config_data.get(ATTR_GATEWAY),
            [
                AddressData(address.get(ATTR_ADDRESS), address.get(ATTR_PREFIX))
                for address in ip4_config_data.get(ATTR_ADDRESS_DATA, [])
            ],
        )
