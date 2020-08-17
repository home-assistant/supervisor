"""Connection object for Network Manager."""
import logging
from typing import Optional

from ...utils.gdbus import DBus
from .configuration import IpConfiguration, NetworkAttributes
from .const import DBUS_NAME_IP4CONFIG, DBUS_NAME_NM, DBUS_NAME_SETTINGS_CONNECTION
from .settings import NetworkSettings

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
        return self._properties["Default"]

    @property
    def id(self) -> str:
        """Return the id of the connection."""
        return self._properties["Id"]

    @property
    def type(self) -> str:
        """Return the type of the connection."""
        return self._properties["Type"]

    @property
    def ip4_config(self) -> IpConfiguration:
        """Return a ip configuration object for the connection."""
        return self._ip4_config

    @property
    def uuid(self) -> str:
        """Return the uuid of the connection."""
        return self._properties["Uuid"]

    @property
    def state(self) -> int:
        """
        Return the state of the connection.

        https://developer.gnome.org/NetworkManager/stable/nm-dbus-types.html#NMActiveConnectionState
        """
        return self._properties["State"]

    async def update_information(self):
        """Update the information for childs ."""
        connection_path = self._properties["Connection"]
        ip4config_path = self._properties["Ip4Config"]

        settings = await DBus.connect(DBUS_NAME_NM, connection_path)
        ip4_config = await DBus.connect(DBUS_NAME_NM, ip4config_path)

        settings_data = await settings.get_properties(DBUS_NAME_SETTINGS_CONNECTION)
        ip4_config_data = await ip4_config.get_properties(DBUS_NAME_IP4CONFIG)

        self._settings = NetworkSettings(connection_path, settings_data)
        self._ip4_config = IpConfiguration(ip4config_path, ip4_config_data)
