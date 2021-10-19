"""NetworkInterface object for Network Manager."""
from typing import Optional

from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_ACTIVE_CONNECTION,
    DBUS_ATTR_DEVICE_INTERFACE,
    DBUS_ATTR_DEVICE_TYPE,
    DBUS_ATTR_DRIVER,
    DBUS_ATTR_MANAGED,
    DBUS_IFACE_DEVICE,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    DeviceType,
)
from ..interface import DBusInterfaceProxy
from .connection import NetworkConnection
from .setting import NetworkSetting
from .wireless import NetworkWireless


class NetworkInterface(DBusInterfaceProxy):
    """NetworkInterface object for Network Manager."""

    def __init__(self, nm_dbus: DBus, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self.primary = False

        self._connection: Optional[NetworkConnection] = None
        self._settings: Optional[NetworkSetting] = None
        self._wireless: Optional[NetworkWireless] = None
        self._nm_dbus: DBus = nm_dbus

    @property
    def name(self) -> str:
        """Return interface name."""
        return self.properties[DBUS_ATTR_DEVICE_INTERFACE]

    @property
    def type(self) -> int:
        """Return interface type."""
        return self.properties[DBUS_ATTR_DEVICE_TYPE]

    @property
    def driver(self) -> str:
        """Return interface driver."""
        return self.properties[DBUS_ATTR_DRIVER]

    @property
    def managed(self) -> bool:
        """Return interface driver."""
        return self.properties[DBUS_ATTR_MANAGED]

    @property
    def connection(self) -> Optional[NetworkConnection]:
        """Return the connection used for this interface."""
        return self._connection

    @property
    def settings(self) -> Optional[NetworkSetting]:
        """Return the connection settings used for this interface."""
        return self._settings

    @property
    def wireless(self) -> Optional[NetworkWireless]:
        """Return the wireless data for this interface."""
        return self._wireless

    async def connect(self) -> None:
        """Get device information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        self.properties = await self.dbus.get_properties(DBUS_IFACE_DEVICE)

        # Abort if device is not managed
        if not self.managed:
            return

        # If active connection exists
        if self.properties[DBUS_ATTR_ACTIVE_CONNECTION] != DBUS_OBJECT_BASE:
            self._connection = NetworkConnection(
                self.properties[DBUS_ATTR_ACTIVE_CONNECTION]
            )
            await self._connection.connect()

        # Attach settings
        if self.connection and self.connection.setting_object != DBUS_OBJECT_BASE:
            self._settings = NetworkSetting(self.connection.setting_object)
            await self._settings.connect()

        # Wireless
        if self.type == DeviceType.WIRELESS:
            self._wireless = NetworkWireless(self.object_path)
            await self._wireless.connect()
