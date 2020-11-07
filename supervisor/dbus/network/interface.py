"""NetworkInterface object for Network Manager."""
from typing import Any, Dict, Optional

from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_ACTIVE_CONNECTION,
    DBUS_ATTR_DEVICE_INTERFACE,
    DBUS_ATTR_DEVICE_TYPE,
    DBUS_ATTR_DRIVER,
    DBUS_ATTR_MANAGED,
    DBUS_NAME_CONNECTION_ACTIVE,
    DBUS_NAME_DEVICE,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
    ConnectionType,
)
from ..interface import DBusInterfaceProxy
from .connection import NetworkConnection
from .setting import NetworkSetting


class NetworkInterface(DBusInterfaceProxy):
    """NetworkInterface object for Network Manager."""

    def __init__(self, nm_dbus: DBus, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self.primary = True

        self._connection: Optional[NetworkConnection] = None
        self._setting: Optional[NetworkSetting] = None
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

    async def connect(self) -> None:
        """Get device information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        self.properties = await self.dbus.get_properties(DBUS_NAME_DEVICE)

        # Abort if device is not managed
        if not self.managed:
            return

        # If connection exists
        if self.properties[DBUS_ATTR_ACTIVE_CONNECTION] != DBUS_OBJECT_BASE:
            self._connection = NetworkConnection(
                self.properties[DBUS_ATTR_ACTIVE_CONNECTION]
            )
            await self._connection.connect()

        # Attach settings
        if self.connection and self.connection.setting_object != DBUS_OBJECT_BASE:
            self._setting = NetworkSetting(self.connection.setting_object)
            await self._setting.connect()

    async def update_settings(self, nm_payload: str) -> None:
        """Update IP configuration used for this interface."""
        await self.connection.settings.dbus.Settings.Connection.Update(nm_payload)

        await self._nm_dbus.ActivateConnection(
            self.connection.settings.dbus.object_path,
            self.dbus.object_path,
            DBUS_OBJECT_BASE,
        )
