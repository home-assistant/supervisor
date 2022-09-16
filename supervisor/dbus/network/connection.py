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
        self.object_path: str = object_path
        self.properties: dict[str, Any] = {}

        self._ipv4: IpConfiguration | None = None
        self._ipv6: IpConfiguration | None = None
        self._state_flags: set[ConnectionStateFlags] = {ConnectionStateFlags.NONE}
        self._settings: NetworkSetting | None = None

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

    @property
    def ipv4(self) -> IpConfiguration | None:
        """Return a ip4 configuration object for the connection."""
        return self._ipv4

    @property
    def ipv6(self) -> IpConfiguration | None:
        """Return a ip6 configuration object for the connection."""
        return self._ipv6

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update connection information."""
        await super().update(changed)

        # State Flags
        self._state_flags = {
            flag
            for flag in ConnectionStateFlags
            if flag.value & self.properties[DBUS_ATTR_STATE_FLAGS]
        } or {ConnectionStateFlags.NONE}

        # IPv4
        if not changed or DBUS_ATTR_IP4CONFIG in changed:
            if self.properties[DBUS_ATTR_IP4CONFIG] != DBUS_OBJECT_BASE:
                self._ipv4 = IpConfiguration(self.properties[DBUS_ATTR_IP4CONFIG])
                await self._ipv4.connect(self.dbus.bus)
            else:
                self._ipv4 = None

        # IPv6
        if not changed or DBUS_ATTR_IP6CONFIG in changed:
            if self.properties[DBUS_ATTR_IP6CONFIG] != DBUS_OBJECT_BASE:
                self._ipv6 = IpConfiguration(
                    self.properties[DBUS_ATTR_IP6CONFIG], False
                )
                await self._ipv6.connect(self.dbus.bus)
            else:
                self._ipv6 = None

        # Settings
        if not changed or DBUS_ATTR_CONNECTION in changed:
            if self.properties[DBUS_ATTR_CONNECTION] != DBUS_OBJECT_BASE:
                self._settings = NetworkSetting(self.properties[DBUS_ATTR_CONNECTION])
                await self._settings.connect(self.dbus.bus)
            else:
                self._settings = None

    def disconnect(self) -> None:
        """Disconnect from D-Bus."""
        if self.ipv4:
            self.ipv4.disconnect()
        if self.ipv6:
            self.ipv6.disconnect()
        if self.settings:
            self.settings.disconnect()
        super().disconnect()
