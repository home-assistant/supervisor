"""Connection object for Network Manager."""
from typing import Any, Awaitable, Optional

from ...utils.gdbus import DBus
from ..const import (
    DBUS_ATTR_ACTIVE_ACCESSPOINT,
    DBUS_NAME_DEVICE_WIRELESS,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
)
from ..interface import DBusInterfaceProxy
from ..utils import dbus_connected
from .accesspoint import NetworkWirelessAP


class NetworkWireless(DBusInterfaceProxy):
    """NetworkWireless object for Network Manager."""

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self._active: Optional[NetworkWirelessAP] = None

    @property
    def active(self) -> Optional[NetworkWirelessAP]:
        """Return details about active connection."""
        return self._active

    @dbus_connected
    def request_scan(self) -> Awaitable[None]:
        """Request a new AP scan."""
        return self.dbus.Device.Wireless.RequestScan("{}")

    @dbus_connected
    def get_all_accesspoints(self) -> Awaitable[Any]:
        """Return a list of all access points path."""
        return self.dbus.Device.Wireless.GetAllAccessPoints()

    async def connect(self) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(DBUS_NAME_NM, self.object_path)
        self.properties = await self.dbus.get_properties(DBUS_NAME_DEVICE_WIRELESS)

        # Get details from current active
        if self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT] != DBUS_OBJECT_BASE:
            self._active = NetworkWirelessAP(
                self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT]
            )
            await self._active.connect()
