"""Interface class for D-Bus wrappers."""
import logging
from typing import Dict, Optional, List

from dbus_next.aio import MessageBus, ProxyInterface, ProxyObject
from dbus_next.introspection import Node

from ..exceptions import DBusError, DBusNotConnectedError

_LOGGER = logging.getLogger(__name__)


class DBusInterface:
    """Handle D-Bus interface for hostname/system."""

    bus_name: Optional[str] = None
    bus_path: Optional[str] = None
    bus_interface: Optional[str] = None
    interface_property: Optional[List[str]] = None

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
        try:
            self.introspection = await self.dbus.introspect(
                self.bus_name, self.bus_path
            )
            self.object = self.dbus.get_proxy_object(
                self.bus_name, self.bus_path, self.introspection
            )
            self.interface = self.object.get_interface(self.bus_interface)
        except TypeError:
            _LOGGER.warning("Can't connect to %s", self.bus_name)

    async def get_property(self):
        """Return list of values."""
        data: Dict[str, str] = {}

        # Guard
        if not self.interface_property:
            _LOGGER.error("%s have no properties", self.bus_name)
            raise DBusError()
        if not self.is_connected:
            _LOGGER.warning("%s is not connected", self.bus_name)
            raise DBusNotConnectedError()

        # Get data
        # pylint: disable=not-an-iterable
        for prop in self.interface_property:
            property_coro = getattr(self.interface, f"get_{prop.lower()}")
            data[prop] = await property_coro()
