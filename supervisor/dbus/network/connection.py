"""Connection object for Network Manager."""

from typing import Any

from supervisor.dbus.network.setting import NetworkSetting

from ..const import (
    DBUS_ATTR_CONNECTION,
    DBUS_ATTR_ID,
    DBUS_ATTR_IP4CONFIG,
    DBUS_ATTR_IP6CONFIG,
    DBUS_ATTR_STATE,
    DBUS_ATTR_STATE_FLAGS,
    DBUS_ATTR_TYPE,
    DBUS_ATTR_UUID,
    DBUS_IFACE_CONNECTION_ACTIVE,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    ConnectionStateFlags,
    ConnectionStateType,
)
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .ip_configuration import IpConfiguration


class NetworkConnection(DBusInterfaceProxy):
    """Active network connection object for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Connection.Active.html
    """

    bus_name: str = DBUS_NAME_NM
    properties_interface: str = DBUS_IFACE_CONNECTION_ACTIVE

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self._object_path: str = object_path
        self._ipv4: IpConfiguration | None = None
        self._ipv6: IpConfiguration | None = None
        self._state_flags: set[ConnectionStateFlags] = {ConnectionStateFlags.NONE}
        self._settings: NetworkSetting | None = None
        super().__init__()

    @property
    def object_path(self) -> str:
        """Object path for dbus object."""
        return self._object_path

    @property
    @dbus_property
    def id(self) -> str:
        """Return the id of the connection."""
        return self.properties[DBUS_ATTR_ID]

    @property
    @dbus_property
    def type(self) -> str:
        """Return the type of the connection."""
        return self.properties[DBUS_ATTR_TYPE]

    @property
    @dbus_property
    def uuid(self) -> str:
        """Return the uuid of the connection."""
        return self.properties[DBUS_ATTR_UUID]

    @property
    @dbus_property
    def state(self) -> ConnectionStateType:
        """Return the state of the connection."""
        return self.properties[DBUS_ATTR_STATE]

    @property
    def state_flags(self) -> set[ConnectionStateFlags]:
        """Return state flags of the connection."""
        return self._state_flags

    @property
    def settings(self) -> NetworkSetting | None:
        """Return settings."""
        return self._settings

    @settings.setter
    def settings(self, settings: NetworkSetting | None) -> None:
        """Set settings."""
        if self._settings and self._settings is not settings:
            self._settings.shutdown()

        self._settings = settings

    @property
    def ipv4(self) -> IpConfiguration | None:
        """Return a ip4 configuration object for the connection."""
        return self._ipv4

    @ipv4.setter
    def ipv4(self, ipv4: IpConfiguration | None) -> None:
        """Set ipv4 configuration."""
        if self._ipv4 and self._ipv4 is not ipv4:
            self._ipv4.shutdown()

        self._ipv4 = ipv4

    @property
    def ipv6(self) -> IpConfiguration | None:
        """Return a ip6 configuration object for the connection."""
        return self._ipv6

    @ipv6.setter
    def ipv6(self, ipv6: IpConfiguration | None) -> None:
        """Set ipv6 configuration."""
        if self._ipv6 and self._ipv6 is not ipv6:
            self._ipv6.shutdown()

        self._ipv6 = ipv6

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update connection information."""
        await super().update(changed)

        # State Flags
        self._state_flags = {
            flag
            for flag in ConnectionStateFlags
            if flag & self.properties[DBUS_ATTR_STATE_FLAGS]
        } or {ConnectionStateFlags.NONE}

        # IPv4
        if not changed or DBUS_ATTR_IP4CONFIG in changed:
            if (
                self.ipv4
                and self.ipv4.is_connected
                and self.ipv4.object_path == self.properties[DBUS_ATTR_IP4CONFIG]
            ):
                await self.ipv4.update()
            elif self.properties[DBUS_ATTR_IP4CONFIG] != DBUS_OBJECT_BASE:
                self.ipv4 = IpConfiguration(self.properties[DBUS_ATTR_IP4CONFIG])
                await self.ipv4.connect(self.connected_dbus.bus)
            else:
                self.ipv4 = None

        # IPv6
        if not changed or DBUS_ATTR_IP6CONFIG in changed:
            if (
                self.ipv6
                and self.ipv6.is_connected
                and self.ipv6.object_path == self.properties[DBUS_ATTR_IP6CONFIG]
            ):
                await self.ipv6.update()
            elif self.properties[DBUS_ATTR_IP6CONFIG] != DBUS_OBJECT_BASE:
                self.ipv6 = IpConfiguration(self.properties[DBUS_ATTR_IP6CONFIG], False)
                await self.ipv6.connect(self.connected_dbus.bus)
            else:
                self.ipv6 = None

        # Settings
        if not changed or DBUS_ATTR_CONNECTION in changed:
            if (
                self.settings
                and self.settings.is_connected
                and self.settings.object_path == self.properties[DBUS_ATTR_CONNECTION]
            ):
                await self.settings.reload()
            elif self.properties[DBUS_ATTR_CONNECTION] != DBUS_OBJECT_BASE:
                self.settings = NetworkSetting(self.properties[DBUS_ATTR_CONNECTION])
                await self.settings.connect(self.connected_dbus.bus)
            else:
                self.settings = None

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        if self.ipv4:
            self.ipv4.shutdown()
        if self.ipv6:
            self.ipv6.shutdown()
        if self.settings:
            self.settings.shutdown()
        super().shutdown()
