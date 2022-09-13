"""DBus implementation with glib."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Awaitable, Callable

from dbus_next import ErrorType, InvalidIntrospectionError, Message, MessageType
from dbus_next.aio.message_bus import MessageBus
from dbus_next.aio.proxy_object import ProxyInterface, ProxyObject
from dbus_next.errors import DBusError
from dbus_next.introspection import Node
from dbus_next.signature import Variant

from ..exceptions import (
    DBusFatalError,
    DBusInterfaceError,
    DBusInterfaceMethodError,
    DBusInterfacePropertyError,
    DBusInterfaceSignalError,
    DBusNotConnectedError,
    DBusObjectError,
    DBusParseError,
    DBusTimeoutError,
    HassioNotSupportedError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_INTERFACE_PROPERTIES: str = "org.freedesktop.DBus.Properties"
DBUS_METHOD_GETALL: str = "org.freedesktop.DBus.Properties.GetAll"


class DBus:
    """DBus handler."""

    def __init__(self, bus: MessageBus, bus_name: str, object_path: str) -> None:
        """Initialize dbus object."""
        self.bus_name: str = bus_name
        self.object_path: str = object_path
        self._proxy_obj: ProxyObject | None = None
        self._proxies: dict[str, ProxyInterface] = {}
        self._bus: MessageBus = bus

    @staticmethod
    async def connect(bus: MessageBus, bus_name: str, object_path: str) -> DBus:
        """Read object data."""
        self = DBus(bus, bus_name, object_path)

        # pylint: disable=protected-access
        await self._init_proxy()

        _LOGGER.debug("Connect to D-Bus: %s - %s", bus_name, object_path)
        return self

    @staticmethod
    def remove_dbus_signature(data: Any) -> Any:
        """Remove signature info."""
        if isinstance(data, Variant):
            return DBus.remove_dbus_signature(data.value)
        elif isinstance(data, dict):
            for k in data:
                data[k] = DBus.remove_dbus_signature(data[k])
            return data
        elif isinstance(data, list):
            new_list = []
            for item in data:
                new_list.append(DBus.remove_dbus_signature(item))
            return new_list
        else:
            return data

    @staticmethod
    def from_dbus_error(err: DBusError) -> HassioNotSupportedError | DBusError:
        """Return correct dbus error based on type."""
        if err.type in {ErrorType.SERVICE_UNKNOWN, ErrorType.UNKNOWN_INTERFACE}:
            return DBusInterfaceError(err.text)
        if err.type in {
            ErrorType.UNKNOWN_METHOD,
            ErrorType.INVALID_SIGNATURE,
            ErrorType.INVALID_ARGS,
        }:
            return DBusInterfaceMethodError(err.text)
        if err.type == ErrorType.UNKNOWN_OBJECT:
            return DBusObjectError(err.text)
        if err.type in {ErrorType.UNKNOWN_PROPERTY, ErrorType.PROPERTY_READ_ONLY}:
            return DBusInterfacePropertyError(err.text)
        if err.type == ErrorType.DISCONNECTED:
            return DBusNotConnectedError(err.text)
        if err.type == ErrorType.TIMEOUT:
            return DBusTimeoutError(err.text)
        return DBusFatalError(err.text)

    @staticmethod
    async def call_dbus(
        proxy_interface: ProxyInterface,
        method: str,
        *args,
        remove_signature: bool = True,
    ) -> Any:
        """Call a dbus method and handle the signature and errors."""
        _LOGGER.debug(
            "D-Bus call - %s.%s on %s",
            proxy_interface.introspection.name,
            method,
            proxy_interface.path,
        )
        try:
            body = await getattr(proxy_interface, method)(*args)
            return DBus.remove_dbus_signature(body) if remove_signature else body
        except DBusError as err:
            raise DBus.from_dbus_error(err)

    def _add_interfaces(self):
        """Make proxy interfaces out of introspection data."""
        self._proxies = {
            interface.name: self._proxy_obj.get_interface(interface.name)
            for interface in self._proxy_obj.introspection.interfaces
        }

    async def _init_proxy(self) -> None:
        """Read interface data."""
        introspection: Node | None = None

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

        self._proxy_obj = self.bus.get_proxy_object(
            self.bus_name, self.object_path, introspection
        )
        self._add_interfaces()

    @property
    def bus(self) -> MessageBus:
        """Get message bus."""
        return self._bus

    async def get_properties(self, interface: str) -> dict[str, Any]:
        """Read all properties from interface."""
        return await DBus.call_dbus(
            self._proxies[DBUS_INTERFACE_PROPERTIES], "call_get_all", interface
        )

    def signal(self, signal_member: str) -> DBusSignalWrapper:
        """Get signal context manager for this object."""
        return DBusSignalWrapper(self, signal_member)

    def __getattr__(self, name: str) -> DBusCallWrapper:
        """Map to dbus method."""
        return getattr(DBusCallWrapper(self, self.bus_name), name)


class DBusCallWrapper:
    """Wrapper a DBus interface for a call."""

    def __init__(self, dbus: DBus, interface: str) -> None:
        """Initialize wrapper."""
        self.dbus: DBus = dbus
        self.interface: str = interface
        self._proxy: ProxyInterface | None = self.dbus._proxies.get(self.interface)

    def __call__(self) -> None:
        """Catch this method from being called."""
        _LOGGER.error("D-Bus method %s not exists!", self.interface)
        raise DBusInterfaceMethodError()

    def __getattr__(self, name: str) -> Awaitable | Callable:
        """Map to dbus method."""
        if not self._proxy:
            return DBusCallWrapper(self.dbus, f"{self.interface}.{name}")

        dbus_type = name.split("_", 1)[0]

        if not hasattr(self._proxy, name):
            message = f"{name} does not exist in D-Bus interface {self.interface}!"
            if dbus_type == "call":
                raise DBusInterfaceMethodError(message, _LOGGER.error)
            if dbus_type == "get":
                raise DBusInterfacePropertyError(message, _LOGGER.error)
            if dbus_type == "set":
                raise DBusInterfacePropertyError(message, _LOGGER.error)
            if dbus_type in ["on", "off"]:
                raise DBusInterfaceSignalError(message, _LOGGER.error)

        # Not much can be done with these currently. *args callbacks aren't supported so can't wrap it
        if dbus_type in ["on", "off"]:
            _LOGGER.debug(
                "D-Bus signal monitor - %s.%s on %s",
                self.interface,
                name,
                self.dbus.object_path,
            )
            return self._method

        if dbus_type in ["call", "get", "set"]:

            def _method_wrapper(*args, remove_signature: bool = True) -> Awaitable:
                return DBus.call_dbus(
                    self._proxy, name, *args, remove_signature=remove_signature
                )

            return _method_wrapper

        # Didn't reach the dbus call yet, just happened to hit another interface. Return a wrapper
        return DBusCallWrapper(self.dbus, f"{self.interface}.{name}")


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

    async def wait_for_signal(self) -> Any:
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
