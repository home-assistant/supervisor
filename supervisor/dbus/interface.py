"""Interface class for D-Bus wrappers."""
from abc import ABC, abstractmethod
from functools import wraps
from typing import Any, Optional

from ..utils.dbus_next import DBus


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

    dbus: Optional[DBus] = None
    name: Optional[str] = None

    @property
    def is_connected(self):
        """Return True, if they is connected to D-Bus."""
        return self.dbus is not None

    @abstractmethod
    async def connect(self):
        """Connect to D-Bus."""

    def disconnect(self):
        """Disconnect from D-Bus."""
        self.dbus = None


class DBusInterfaceProxy(ABC):
    """Handle D-Bus interface proxy."""

    dbus: Optional[DBus] = None
    object_path: Optional[str] = None
    properties: Optional[dict[str, Any]] = None

    @abstractmethod
    async def connect(self):
        """Connect to D-Bus."""
