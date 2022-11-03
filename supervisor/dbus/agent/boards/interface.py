"""Board dbus proxy interface."""

from typing import Any

from ...const import DBUS_IFACE_HAOS_BOARDS, DBUS_NAME_HAOS, DBUS_OBJECT_HAOS_BOARDS
from ...interface import DBusInterfaceProxy


class BoardProxy(DBusInterfaceProxy):
    """DBus interface proxy for os board."""

    bus_name: str = DBUS_NAME_HAOS

    def __init__(self, name: str) -> None:
        """Initialize properties."""
        self._name: str = name
        self.object_path: str = f"{DBUS_OBJECT_HAOS_BOARDS}/{name}"
        self.properties_interface: str = f"{DBUS_IFACE_HAOS_BOARDS}.{name}"
        self.properties: dict[str, Any] = {}

    @property
    def name(self) -> str:
        """Get name."""
        return self._name
