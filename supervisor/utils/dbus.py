"""DBus implementation with glib."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from dbus_next import BusType, InvalidIntrospectionError, Message, MessageType
from dbus_next.aio import MessageBus
from dbus_next.introspection import Node
from dbus_next.signature import Variant

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
        self._bus: MessageBus | None = None

    def __del__(self):
        """Delete dbus object."""
        if self._bus:
            self._bus.disconnect()

    @staticmethod
    async def connect(bus_name: str, object_path: str) -> DBus:
        """Read object data."""
        self = DBus(bus_name, object_path)

        # pylint: disable=protected-access
        await self._init_proxy()

        _LOGGER.debug("Connect to D-Bus: %s - %s", bus_name, object_path)
        return self

    def _add_interfaces(self, introspection: Any):
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

    async def _init_proxy(self) -> None:
        """Read interface data."""
        # Wait for dbus object to be available after restart
        introspection: Node | None = None
        try:
            self._bus = await MessageBus(bus_type=BusType.SYSTEM).connect()
        except Exception as err:
            raise DBusFatalError() from err

        for _ in range(3):
            try:
                introspection = await self._bus.introspect(
                    self.bus_name, self.object_path, timeout=10
                )
            except InvalidIntrospectionError as err:
                raise DBusParseError(
                    f"Can't parse introspect data: {err}", _LOGGER.error
                ) from err
            except (EOFError, asyncio.TimeoutError):
                _LOGGER.warning(
                    "Busy system at %s - %s", self.bus_name, self.object_path
                )
            else:
                break

            await asyncio.sleep(3)

        if introspection is None:
            raise DBusFatalError(
                "Could not get introspection data after 3 attempts", _LOGGER.error
            )

        self._add_interfaces(introspection)

    def _prepare_args(self, *args: list[Any]) -> tuple[str, list[Any]]:
        signature = ""
        arg_list = []

        for arg in args:
            _LOGGER.debug("...arg %s (type %s)", str(arg), type(arg))
            if isinstance(arg, bool):
                signature += "b"
                arg_list.append(arg)
            elif isinstance(arg, int):
                signature += "i"
                arg_list.append(arg)
            elif isinstance(arg, float):
                signature += "d"
                arg_list.append(arg)
            elif isinstance(arg, str):
                signature += "s"
                arg_list.append(arg)
            elif isinstance(arg, tuple):
                signature += arg[0]
                arg_list.append(arg[1])
            else:
                raise DBusFatalError(f"Type {type(arg)} not supported")

        return signature, arg_list

    async def call_dbus(self, method: str, *args: list[Any]) -> str:
        """Call a dbus method."""
        method_parts = method.split(".")

        signature, arg_list = self._prepare_args(*args)

        _LOGGER.debug("Call %s on %s", method, self.object_path)
        reply = await self._bus.call(
            Message(
                destination=self.bus_name,
                path=self.object_path,
                interface=".".join(method_parts[:-1]),
                member=method_parts[-1],
                signature=signature,
                body=arg_list,
            )
        )

        if reply.message_type == MessageType.ERROR:
            if reply.error_name == "org.freedesktop.DBus.Error.ServiceUnknown":
                raise DBusInterfaceError(reply.body[0])
            if reply.error_name == "org.freedesktop.DBus.Error.UnknownMethod":
                raise DBusInterfaceMethodError(reply.body[0])
            if reply.error_name == "org.freedesktop.DBus.Error.Disconnected":
                raise DBusNotConnectedError()
            if reply.body and len(reply.body) > 0:
                raise DBusFatalError(reply.body[0])
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
        self,
        interface: str,
        name: str,
        value: Any,
    ) -> dict[str, Any] | None:
        """Set a property from interface."""
        return await self.call_dbus(DBUS_METHOD_SET, interface, name, value)

    def signal(self, signal_member) -> DBusSignalWrapper:
        """Get signal context manager for this object."""
        return DBusSignalWrapper(self, signal_member)

    async def wait_signal(self, signal_member) -> Any:
        """Wait for signal on this object."""
        async with self.signal(signal_member) as signal:
            return await signal.wait_for_signal()

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


class DBusSignalWrapper:
    """Wrapper for D-Bus Signal."""

    def __init__(self, dbus: DBus, signal_member: str) -> None:
        """Initialize wrapper."""
        self._dbus: DBus = dbus
        signal_parts = signal_member.split(".")
        self._interface = ".".join(signal_parts[:-1])
        self._member = signal_parts[-1]
        self._match: str = f"type='signal',interface={self._interface},member={self._member},path={self._dbus.object_path}"
        self._messages: asyncio.Queue[Message] = asyncio.Queue()

    def _message_handler(self, msg: Message):
        if msg.message_type != MessageType.SIGNAL:
            return

        _LOGGER.debug(
            "Signal message received %s, %s.%s object %s",
            msg.body,
            msg.interface,
            msg.member,
            msg.path,
        )
        if (
            msg.interface != self._interface
            or msg.member != self._member
            or msg.path != self._dbus.object_path
        ):
            return

        self._messages.put_nowait(msg)

    async def __aenter__(self):
        """Install match for signals and start collecting signal messages."""

        _LOGGER.debug("Install match for signal %s.%s", self._interface, self._member)
        await self._dbus._bus.call(
            Message(
                destination="org.freedesktop.DBus",
                interface="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                member="AddMatch",
                signature="s",
                body=[self._match],
            )
        )

        self._dbus._bus.add_message_handler(self._message_handler)
        return self

    async def wait_for_signal(self) -> Message:
        """Wait for signal and returns signal payload."""
        msg = await self._messages.get()
        return msg.body

    async def __aexit__(self, exc_t, exc_v, exc_tb):
        """Stop collecting signal messages and remove match for signals."""

        self._dbus._bus.remove_message_handler(self._message_handler)

        await self._dbus._bus.call(
            Message(
                destination="org.freedesktop.DBus",
                interface="org.freedesktop.DBus",
                path="/org/freedesktop/DBus",
                member="RemoveMatch",
                signature="s",
                body=[self._match],
            )
        )
