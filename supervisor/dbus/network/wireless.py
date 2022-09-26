"""Wireless object for Network Manager."""
import asyncio
import logging
from typing import Any

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

    bus_name: str = DBUS_NAME_NM
    properties_interface: str = DBUS_IFACE_DEVICE_WIRELESS

    def __init__(self, object_path: str) -> None:
        """Initialize NetworkConnection object."""
        self.object_path: str = object_path
        self.properties: dict[str, Any] = {}

        self._active: NetworkWirelessAP | None = None

    @property
    def active(self) -> NetworkWirelessAP | None:
        """Return details about active connection."""
        return self._active

    @active.setter
    def active(self, active: NetworkWirelessAP | None) -> None:
        """Set active wireless AP."""
        if self._active and self._active is not active:
            self._active.shutdown()

        self._active = active

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

    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        await super().update(changed)

        # Get details from current active
        if not changed or DBUS_ATTR_ACTIVE_ACCESSPOINT in changed:
            if (
                self.active
                and self.active.is_connected
                and self.active.object_path
                == self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT]
            ):
                await self.active.update()
            elif self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT] != DBUS_OBJECT_BASE:
                self.active = NetworkWirelessAP(
                    self.properties[DBUS_ATTR_ACTIVE_ACCESSPOINT]
                )
                await self.active.connect(self.dbus.bus)
            else:
                self.active = None
