"""NetworkInterface object for Network Manager."""

from typing import Any

from dbus_next.aio.message_bus import MessageBus

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
from ..interface import DBusInterfaceProxy, dbus_property
from ..utils import dbus_connected
from .connection import NetworkConnection
from .setting import NetworkSetting
from .wireless import NetworkWireless


class NetworkInterface(DBusInterfaceProxy):
    """NetworkInterface object represents Network Manager Device objects.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Device.html
    """

    bus_name: str = DBUS_NAME_NM
    properties_interface: str = DBUS_IFACE_DEVICE

    def __init__(self, nm_dbus: DBus, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path: str = object_path
        self.properties: dict[str, Any] = {}

        self.primary: bool = False

        self._connection: NetworkConnection | None = None
        self._wireless: NetworkWireless | None = None
        self._nm_dbus: DBus = nm_dbus

    @property
    @dbus_property
    def name(self) -> str:
        """Return interface name."""
        return self.properties[DBUS_ATTR_DEVICE_INTERFACE]

    @property
    @dbus_property
    def type(self) -> int:
        """Return interface type."""
        return self.properties[DBUS_ATTR_DEVICE_TYPE]

    @property
    @dbus_property
    def driver(self) -> str:
        """Return interface driver."""
        return self.properties[DBUS_ATTR_DRIVER]

    @property
    @dbus_property
    def managed(self) -> bool:
        """Return interface driver."""
        return self.properties[DBUS_ATTR_MANAGED]

    @property
    def connection(self) -> NetworkConnection | None:
        """Return the connection used for this interface."""
        return self._connection

    @property
    def settings(self) -> NetworkSetting | None:
        """Return the connection settings used for this interface."""
        return self.connection.settings if self.connection else None

    @property
    def wireless(self) -> NetworkWireless | None:
        """Return the wireless data for this interface."""
        return self._wireless

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        return await super().connect(bus)

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        await super().update(changed)

        # Abort if device is not managed
        if not self.managed:
            return

        # If active connection exists
        if not changed or DBUS_ATTR_ACTIVE_CONNECTION in changed:
            if self.properties[DBUS_ATTR_ACTIVE_CONNECTION] != DBUS_OBJECT_BASE:
                self._connection = NetworkConnection(
                    self.properties[DBUS_ATTR_ACTIVE_CONNECTION]
                )
                await self._connection.connect(self.dbus.bus)
            else:
                self._connection = None

        # Wireless
        if not changed and self.type == DeviceType.WIRELESS:
            if not self.wireless:
                self._wireless = NetworkWireless(self.object_path)
                await self._wireless.connect(self.dbus.bus)
            else:
                self._wireless.update()

    def disconnect(self) -> None:
        """Disconnect from D-Bus."""
        if self.connection:
            self.connection.disconnect()
        if self.wireless:
            self.wireless.disconnect()
        super().disconnect()
