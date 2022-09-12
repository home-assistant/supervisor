"""Interface class for D-Bus wrappers."""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any

from dbus_next.aio.message_bus import MessageBus

from ..utils.dbus import DBus


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

    @property
    def is_connected(self):
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    @abstractmethod
    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""

    def disconnect(self):
        """Disconnect from D-Bus."""
        self.dbus = None


class DBusInterfaceProxy(ABC):
    """Handle D-Bus interface proxy."""

    dbus: DBus | None = None
    object_path: str | None = None
    properties: dict[str, Any] | None = None

    @abstractmethod
    async def connect(self, bus: MessageBus):
        """Connect to D-Bus."""
