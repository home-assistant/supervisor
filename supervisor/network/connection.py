"""Connection object for Network Manager."""
import logging
from typing import Optional

from ..dbus.utils import DBus
from .const import DBUS_NAME_NM
from .ipconfig import NetworkSettingsIPConfig
from .network_attributes import NetworkAttributes
from .settings import NetworkSettings

_LOGGER = logging.getLogger(__name__)


class NetworkConnection(NetworkAttributes):
    """NetworkConnection object for Network Manager."""

    def __init__(self, object_path: str, properties: dict) -> None:
        """Initialize NetworkConnection object."""
        super().__init__(object_path, properties)
        self._settings: Optional[NetworkSettings] = None
        self._ip4_config: Optional[NetworkSettingsIPConfig] = None

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
    def ip4_config(self) -> NetworkSettingsIPConfig:
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
        settings = await DBus.connect(DBUS_NAME_NM, self._properties["Connection"])
        ip4_config = await DBus.connect(DBUS_NAME_NM, self._properties["Ip4Config"])

        settings_data = await settings.get_properties(
            f"{DBUS_NAME_NM}.Settings.Connection"
        )

        ip4_config_data = await ip4_config.get_properties(f"{DBUS_NAME_NM}.IP4Config")

        self._settings = NetworkSettings(self._properties["Connection"], settings_data)
        self._ip4_config = NetworkSettingsIPConfig(
            self._properties["Ip4Config"], ip4_config_data
        )
