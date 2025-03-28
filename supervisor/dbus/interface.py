"""Interface class for D-Bus wrappers."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from functools import wraps
from typing import Any

from dbus_fast.aio.message_bus import MessageBus

from supervisor.exceptions import DBusInterfaceError, DBusNotConnectedError

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
    _shutdown: bool = False

    @property
    @abstractmethod
    def bus_name(self) -> str:
        """Bus name for dbus object."""

    @property
    @abstractmethod
    def object_path(self) -> str:
        """Object path for dbus object."""

    @property
    def is_connected(self) -> bool:
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    @property
    def is_shutdown(self) -> bool:
        """Return True, if the object has been shutdown."""
        return self._shutdown

    @property
    def connected_dbus(self) -> DBus:
        """Return dbus object. Raise if not connected."""
        if not self.dbus:
            raise DBusNotConnectedError()
        return self.dbus

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
            self.connected_dbus.disconnect()
            self.dbus = None

    def shutdown(self) -> None:
        """Shutdown the object and disconnect from D-Bus.

        This method is irreversible.
        """
        self._shutdown = True
        self.disconnect()


class DBusInterfaceProxy(DBusInterface, ABC):
    """Handle D-Bus interface proxy."""

    sync_properties: bool = True
    _sync_properties_callback: Callable | None = None

    def __init__(self) -> None:
        """Initialize properties."""
        self.properties: dict[str, Any] = {}

    @property
    @abstractmethod
    def properties_interface(self) -> str:
        """Primary interface of object to get property values from."""

    async def connect(self, bus: MessageBus) -> None:
        """Connect to D-Bus."""
        await super().connect(bus)

    async def initialize(self, connected_dbus: DBus) -> None:
        """Initialize object with already connected dbus object."""
        await super().initialize(connected_dbus)

        if not self.connected_dbus.properties:
            self.disconnect()
            raise DBusInterfaceError(
                f"D-Bus object {self.object_path} is not usable, introspection is missing required properties interface"
            )

        await self.update()
        if self.sync_properties and self.is_connected:
            self._sync_properties_callback = self.connected_dbus.sync_property_changes(
                self.properties_interface, self.update
            )

    def stop_sync_property_changes(self) -> None:
        """Stop syncing property changes to object."""
        if not self._sync_properties_callback or not self.dbus:
            return

        self.dbus.stop_sync_property_changes(self._sync_properties_callback)
        self.sync_properties = False

    @dbus_connected
    async def update(self, changed: dict[str, Any] | None = None) -> None:
        """Update properties via D-Bus."""
        if changed and self.properties:
            self.properties.update(changed)
        else:
            self.properties = await self.connected_dbus.get_properties(
                self.properties_interface
            )
