"""NetworkInterface object for Network Manager."""

from typing import Any

from dbus_fast.aio.message_bus import MessageBus

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
    sync_properties: bool = False

    def __init__(self, nm_dbus: DBus, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        super().__init__()

        self.object_path: str = object_path

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
    def type(self) -> DeviceType:
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

    @connection.setter
    def connection(self, connection: NetworkConnection | None) -> None:
        """Set connection for interface."""
        if self._connection and self._connection is not connection:
            self._connection.shutdown()

        self._connection = connection

    @property
    def settings(self) -> NetworkSetting | None:
        """Return the connection settings used for this interface."""
        return self.connection.settings if self.connection else None

    @property
    def wireless(self) -> NetworkWireless | None:
        """Return the wireless data for this interface."""
        return self._wireless

    @wireless.setter
    def wireless(self, wireless: NetworkWireless | None) -> None:
        """Set wireless for interface."""
        if self._wireless and self._wireless is not wireless:
            self._wireless.shutdown()

        self._wireless = wireless

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

        self.sync_properties = self.managed
        if self.sync_properties and self.is_connected:
            self.dbus.sync_property_changes(self.properties_interface, self.update)

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        await super().update(changed)

        # Abort if device is not managed
        if not self.managed:
            return

        # If active connection exists
        if not changed or DBUS_ATTR_ACTIVE_CONNECTION in changed:
            if (
                self.connection
                and self.connection.is_connected
                and self.connection.object_path
                == self.properties[DBUS_ATTR_ACTIVE_CONNECTION]
            ):
                await self.connection.update()
            elif self.properties[DBUS_ATTR_ACTIVE_CONNECTION] != DBUS_OBJECT_BASE:
                self.connection = NetworkConnection(
                    self.properties[DBUS_ATTR_ACTIVE_CONNECTION]
                )
                await self.connection.connect(self.dbus.bus)
            else:
                self.connection = None

        # Wireless
        if not changed or DBUS_ATTR_DEVICE_TYPE in changed:
            if self.type != DeviceType.WIRELESS:
                self.wireless = None
            elif self.wireless and self.wireless.is_connected:
                await self.wireless.update()
            else:
                self.wireless = NetworkWireless(self.object_path)
                await self.wireless.connect(self.dbus.bus)

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        if self.connection:
            self.connection.shutdown()
        if self.wireless:
            self.wireless.shutdown()
        super().shutdown()
