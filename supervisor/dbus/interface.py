"""Interface class for D-Bus wrappers."""
from abc import ABC
from collections.abc import Callable
from functools import wraps
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from supervisor.exceptions import DBusInterfaceError

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
    _shutdown: bool = False

    @property
    def is_connected(self) -> bool:
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    @property
    def is_shutdown(self) -> bool:
        """Return True, if the object has been shutdown."""
        return self._shutdown

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await self.initialize(await DBus.connect(bus, self.bus_name, self.object_path))

    async def initialize(self, connected_dbus: DBus) -> None:
        """Initialize object with already connected dbus object."""
        if not connected_dbus.connected:
            raise ValueError("must be a connected DBus object")

        if (
            connected_dbus.bus_name != self.bus_name
            or connected_dbus.object_path != self.object_path
        ):
            raise ValueError(
                f"must be a DBus object connected to bus {self.bus_name} and object {self.object_path}"
            )

        self.dbus = connected_dbus

    def disconnect(self) -> None:
        """Disconnect from D-Bus."""
        if self.is_connected:
            self.dbus.disconnect()
            self.dbus = None

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        self._shutdown = True
        self.disconnect()


class DBusInterfaceProxy(DBusInterface):
    """Handle D-Bus interface proxy."""

    properties_interface: str | None = None
    properties: dict[str, Any] | None = None
    sync_properties: bool = True
    _sync_properties_callback: Callable | None = None

    def __init__(self):
        """Initialize properties."""
        self.properties = {}

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

    async def initialize(self, connected_dbus: DBus) -> None:
        """Initialize object with already connected dbus object."""
        await super().initialize(connected_dbus)

        if not self.dbus.properties:
            self.disconnect()
            raise DBusInterfaceError(
                f"D-Bus object {self.object_path} is not usable, introspection is missing required properties interface"
            )

        await self.update()
        if self.sync_properties and self.is_connected:
            self._sync_properties_callback = self.dbus.sync_property_changes(
                self.properties_interface, self.update
            )

    def stop_sync_property_changes(self) -> None:
        """Stop syncing property changes to object."""
        if not self._sync_properties_callback:
            return

        self.dbus.stop_sync_property_changes(self._sync_properties_callback)
        self.sync_properties = False

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        if changed and self.properties:
            self.properties.update(changed)
        else:
            self.properties = await self.dbus.get_properties(self.properties_interface)
