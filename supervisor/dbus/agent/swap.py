"""Swap object for OS Agent."""

from collections.abc import Awaitable

from ..const import (
    DBUS_ATTR_SWAP_SIZE,
    DBUS_ATTR_SWAPPINESS,
    DBUS_IFACE_HAOS_CONFIG_SWAP,
    DBUS_NAME_HAOS,
    DBUS_OBJECT_HAOS_CONFIG_SWAP,
)
from ..interface import DBusInterfaceProxy, dbus_property


class Swap(DBusInterfaceProxy):
    """Swap object for OS Agent."""

    bus_name: str = DBUS_NAME_HAOS
    object_path: str = DBUS_OBJECT_HAOS_CONFIG_SWAP
    properties_interface: str = DBUS_IFACE_HAOS_CONFIG_SWAP

    @property
    @dbus_property
    def swap_size(self) -> str:
        """Get swap size."""
        return self.properties[DBUS_ATTR_SWAP_SIZE]

    def set_swap_size(self, size: str) -> Awaitable[None]:
        """Set swap size."""
        return self.connected_dbus.Config.Swap.set("swap_size", size)

    @property
    @dbus_property
    def swappiness(self) -> int:
        """Get swappiness."""
        return self.properties[DBUS_ATTR_SWAPPINESS]

    def set_swappiness(self, swappiness: int) -> Awaitable[None]:
        """Set swappiness."""
        return self.connected_dbus.Config.Swap.set("swappiness", swappiness)
