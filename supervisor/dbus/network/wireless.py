"""Connection object for Network Manager."""
from typing import Any, Awaitable, Dict, Optional

from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_ACTIVE_ACCESSPOINT,
    DBUS_ATTR_CONNECTION,
    DBUS_ATTR_FREQUENCY,
    DBUS_ATTR_HWADDRESS,
    DBUS_ATTR_MODE,
    DBUS_ATTR_SSID,
    DBUS_ATTR_STRENGTH,
    DBUS_NAME_ACCESSPOINT,
    DBUS_NAME_DEVICE_WIRELESS,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
)
from ..interface import DBusInterfaceProxy
from ..utils import dbus_connected
from .configuration import APConfiguration


class NetworkWireless(DBusInterfaceProxy):
    """NetworkWireless object for Network Manager."""

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self._active: Optional[APConfiguration] = None

    @property
    def active(self) -> Optional[APConfiguration]:
        """Return details about active connection."""
        return self._active

    @property
    def setting_object(self) -> int:
        """Return the connection object path."""
        return self.properties[DBUS_ATTR_CONNECTION]

    @dbus_connected
    def request_scan(self) -> Awaitable[None]:
        """Request a new AP scan."""
        return self.dbus.Device.Wireless.RequestScan("{}")

    @dbus_connected
    def get_all_accesspoints(self) -> Awaitable[Any]:
        """Return a list of all access points path."""
        return self.dbus.Device.Wireless.GetAllAccessPoints()

    async def object_to_accesspoints(self, object_path: str) -> APConfiguration:
        """Convert an AP object path into object."""
        ap = DBus.connect(DBUS_NAME_NM, object_path)
        data = ap.get_properties(DBUS_NAME_ACCESSPOINT)

        return APConfiguration(
            bytes(data[DBUS_ATTR_SSID]).decode(),
            data[DBUS_ATTR_FREQUENCY],
            data[DBUS_ATTR_HWADDRESS],
            data[DBUS_ATTR_MODE],
            int(bytes(data[DBUS_ATTR_STRENGTH])),
        )

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        self.properties = await self.dbus.get_properties(DBUS_NAME_DEVICE_WIRELESS)

        # Get details from current active
        if self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT] != DBUS_OBJECT_BASE:
            self._active = await self.object_to_accesspoints(
                self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT]
            )
