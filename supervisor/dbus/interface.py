"""Interface class for D-Bus wrappers."""
from abc import ABC
from functools import wraps
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from ..utils.dbus import DBus
from .utils import dbus_connected


def dbus_property(func):
    """Wrap not loaded properties."""

    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except (KeyError, AttributeError):
            return None

    return wrapper


class DBusInterface(ABC):
    """Handle D-Bus interface for hostname/system."""

    dbus: DBus | None = None
    name: str | None = None
    bus_name: str | None = None
    object_path: str | None = None

    @property
    def is_connected(self) -> bool:
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        self.dbus = await DBus.connect(bus, self.bus_name, self.object_path)

    def disconnect(self) -> None:
        """Disconnect from D-Bus."""
        if self.is_connected:
            self.dbus.disconnect()
            self.dbus = None


class DBusInterfaceProxy(DBusInterface):
    """Handle D-Bus interface proxy."""

    properties_interface: str | None = None
    properties: dict[str, Any] | None = None
    sync_properties: bool = True

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)
        await self.update()

        if self.sync_properties:
            self.dbus.sync_property_changes(self.properties_interface, self.update)

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        if changed and self.properties:
            self.properties.update(changed)
        else:
            self.properties = await self.dbus.get_properties(self.properties_interface)
