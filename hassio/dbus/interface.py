"""Interface class for D-Bus wrappers."""
from typing import Optional

from dbus_next.aio import MessageBus, ProxyInterface, ProxyObject
from dbus_next.introspection import Node


class DBusInterface:
    """Handle D-Bus interface for hostname/system."""

    bus_name: Optional[str] = None
    bus_path: Optional[str] = None
    bus_interface: Optional[str] = None

    def __init__(self, dbus: MessageBus):
        """Initialize systemd."""
        self.dbus: MessageBus = None
        self.introspection: Optional[Node] = None
        self.object: Optional[ProxyObject] = None
        self.interface: Optional[ProxyInterface] = None

    @property
    def is_connected(self):
        """Return True, if they is connected to D-Bus."""
        return self.introspection is not None

    async def connect(self):
        """Connect to D-Bus."""
        raise NotImplementedError()
