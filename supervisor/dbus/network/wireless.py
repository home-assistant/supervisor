"""Wireless object for Network Manager."""
import asyncio
import logging

from dbus_next.aio.message_bus import MessageBus

from ...utils.dbus import DBus
from ..const import (
    DBUS_ATTR_ACTIVE_ACCESSPOINT,
    DBUS_IFACE_DEVICE_WIRELESS,
    DBUS_NAME_NM,
    DBUS_OBJECT_BASE,
)
from ..interface import DBusInterfaceProxy
from ..utils import dbus_connected
from .accesspoint import NetworkWirelessAP

_LOGGER: logging.Logger = logging.getLogger(__name__)


class NetworkWireless(DBusInterfaceProxy):
    """Wireless object for Network Manager.

    https://developer.gnome.org/NetworkManager/stable/gdbus-org.freedesktop.NetworkManager.Device.Wireless.html
    """

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path = object_path
        self.properties = {}

        self._active: NetworkWirelessAP | None = None

    @property
    def active(self) -> NetworkWirelessAP | None:
        """Return details about active connection."""
        return self._active

    @dbus_connected
    async def request_scan(self) -> None:
        """Request a new AP scan."""
        await self.dbus.Device.Wireless.call_request_scan({})

    @dbus_connected
    async def get_all_accesspoints(self) -> list[NetworkWirelessAP]:
        """Return a list of all access points path."""
        accesspoints_data = await self.dbus.Device.Wireless.call_get_all_access_points()
        accesspoints = [NetworkWirelessAP(ap_obj) for ap_obj in accesspoints_data]

        for err in await asyncio.gather(
            *[ap.connect(self.dbus.bus) for ap in accesspoints], return_exceptions=True
        ):
            if err:
                _LOGGER.warning("Can't process an AP: %s", err)

        return accesspoints

    async def connect(self, bus: MessageBus) -> None:
        """Get connection information."""
        self.dbus = await DBus.connect(bus, DBUS_NAME_NM, self.object_path)
        self.properties = await self.dbus.get_properties(DBUS_IFACE_DEVICE_WIRELESS)

        # Get details from current active
        if self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT] != DBUS_OBJECT_BASE:
            self._active = NetworkWirelessAP(
                self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT]
            )
            await self._active.connect(bus)
