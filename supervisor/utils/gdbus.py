"""DBus implementation with glib."""
from __future__ import annotations

import asyncio
import logging
from typing import Any
from dbus_next import Message, MessageType, BusType, InvalidIntrospectionError
from dbus_next.signature import Variant
from dbus_next.aio import MessageBus

from ..exceptions import (
    DBusFatalError,
    DBusInterfaceError,
    DBusInterfaceMethodError,
    DBusNotConnectedError,
    DBusParseError,
)

def _remove_dbus_signature(data: Any) -> Any:
    if isinstance(data, Variant):
        return _remove_dbus_signature(data.value)
    elif isinstance(data, dict):
        for k in data:
            data[k] = _remove_dbus_signature(data[k])
        return data
    elif isinstance(data, list):
        new_list = []
        for item in data:
            new_list.append(_remove_dbus_signature(item))
        return new_list
    else:
        return data

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_METHOD_GETALL: str = "org.freedesktop.DBus.Properties.GetAll"
DBUS_METHOD_SET: str = "org.freedesktop.DBus.Properties.Set"

class DBus:
    """DBus handler."""

    def __init__(self, bus_name: str, object_path: str) -> None:
        """Initialize dbus object."""
        self.bus_name: str = bus_name
        self.object_path: str = object_path
        self.methods: set[str] = set()
        self.signals: set[str] = set()

    @staticmethod
    async def connect(bus_name: str, object_path: str) -> DBus:
        """Read object data."""
        self = DBus(bus_name, object_path)

        # pylint: disable=protected-access
        await self._init_proxy()

        _LOGGER.debug("Connect to D-Bus: %s - %s", bus_name, object_path)
        return self

    async def _init_proxy(self) -> None:
        """Read interface data."""
        # Wait for dbus object to be available after restart
        self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()

        try:
            introspection = await self._bus.introspect(self.bus_name, self.object_path, timeout=10)
        except InvalidIntrospectionError as err:
            _LOGGER.error("Can't parse introspect data: %s", err)
            raise DBusParseError() from err

        # Read available methods
        for interface in introspection.interfaces:
            interface_name = interface.name

            # Methods
            for method in interface.methods:
                method_name = method.name
                self.methods.add(f"{interface_name}.{method_name}")

            # Signals
            for signal in interface.signals:
                signal_name = signal.name
                self.signals.add(f"{interface_name}.{signal_name}")

    async def call_dbus(self, method: str, *args: list[Any]) -> str:
        """Call a dbus method."""
        method_parts = method.split(".")
        signature = ""

        for arg in args:
            _LOGGER.debug("...arg %s (type %s)", str(arg), type(arg))
            if isinstance(arg, bool):
                signature += "b"
            elif isinstance(arg, int):
                signature += "i"
            elif isinstance(arg, float):
                signature += "d"
            elif isinstance(arg, str):
                signature += "s"
            else:
                raise DBusFatalError(f"Type %s not supported")

        _LOGGER.debug("Call %s on %s", method, self.object_path)
        reply = await self._bus.call(
            Message(destination=self.bus_name,
                    path=self.object_path,
                    interface=".".join(method_parts[:-1]),
                    member=method_parts[-1],
                    signature=signature,
                    body=[*args]))

        if reply.message_type == MessageType.ERROR:
            if reply.error_name in ("org.freedesktop.DBus.Error.ServiceUnknown", "org.freedesktop.DBus.Error.UnknownMethod"):
                raise DBusInterfaceError(reply.body[0])
            elif reply.error_name == "org.freedesktop.DBus.Error.Disconnected":
                raise DBusNotConnectedError()
            if reply.body and len(reply.body) > 0:
                raise DBusFatalError(reply.body[0])
            else:
                raise DBusFatalError()

        return _remove_dbus_signature(reply.body)

    async def get_properties(self, interface: str) -> dict[str, Any]:
        """Read all properties from interface."""
        try:
            return (await self.call_dbus(DBUS_METHOD_GETALL, interface))[0]
        except IndexError as err:
            _LOGGER.error("No attributes returned for %s", interface)
            raise DBusFatalError() from err

    async def set_property(
        self, interface: str, name: str, value: Any
    ) -> dict[str, Any]:
        """Set a property from interface."""
        try:
            return (await self.call_dbus(DBUS_METHOD_SET, interface, name, value))[0]
        except IndexError as err:
            _LOGGER.error("No Set attribute %s for %s", name, interface)
            raise DBusFatalError() from err

    async def wait_signal(self, signal):
        """Wait for single event."""
        signal_parts = signal.split(".")
        interface = ".".join(signal_parts[:-1])
        member = signal_parts[-1]

        _LOGGER.debug("Wait for signal %s", signal)
        await self._bus.call(
            Message(destination='org.freedesktop.DBus',
                interface='org.freedesktop.DBus',
                path='/org/freedesktop/DBus',
                member='AddMatch',
                signature='s',
                body=[f"type='signal',interface={interface},member={member}"]))

        loop = asyncio.get_event_loop()
        future = loop.create_future()

        def message_handler(msg: Message):
            if msg.message_type != MessageType.SIGNAL:
                return

            _LOGGER.debug("Signal message received %s, %s %s", msg, msg.interface, msg.member)
            if msg.interface != interface or msg.member != member:
                return

            # Avoid race condition: We already received signal but handler not yet removed.
            if future.done():
                return

            future.set_result(_remove_dbus_signature(msg.body))

        self._bus.add_message_handler(message_handler)
        result = await future
        self._bus.remove_message_handler(message_handler)

        return result


    def __getattr__(self, name: str) -> DBusCallWrapper:
        """Map to dbus method."""
        return getattr(DBusCallWrapper(self, self.bus_name), name)


class DBusCallWrapper:
    """Wrapper a DBus interface for a call."""

    def __init__(self, dbus: DBus, interface: str) -> None:
        """Initialize wrapper."""
        self.dbus: DBus = dbus
        self.interface: str = interface

    def __call__(self) -> None:
        """Catch this method from being called."""
        _LOGGER.error("D-Bus method %s not exists!", self.interface)
        raise DBusInterfaceMethodError()

    def __getattr__(self, name: str):
        """Map to dbus method."""
        interface = f"{self.interface}.{name}"

        if interface not in self.dbus.methods:
            return DBusCallWrapper(self.dbus, interface)

        def _method_wrapper(*args):
            """Wrap method.

            Return a coroutine
            """
            return self.dbus.call_dbus(interface, *args)

        return _method_wrapper
