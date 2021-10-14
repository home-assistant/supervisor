"""DBus implementation with glib."""
from __future__ import annotations

import logging
from signal import SIGINT
from typing import Any
import xml.etree.ElementTree as ET

import dbussy
from dbussy import DBUS

from . import clean_env
from ..exceptions import (
    DBusFatalError,
    DBusInterfaceError,
    DBusInterfaceMethodError,
    DBusNotConnectedError,
    DBusParseError,
    DBusProgramError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

DBUS_METHOD_GETALL: str = "org.freedesktop.DBus.Properties.GetAll"
DBUS_METHOD_SET: str = "org.freedesktop.DBus.Properties.Set"


def _remove_dbus_signature(data: Any) -> Any:
    if isinstance(data, tuple) and isinstance(data[0], dbussy.DBUS.Signature):
        return _remove_dbus_signature(data[1])
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
        # """Read interface data."""
        self._conn = await dbussy.Connection.bus_get_async(
            DBUS.BUS_SYSTEM, private=False
        )

        message = dbussy.Message.new_method_call(
            destination=self.bus_name,
            path=self.object_path,
            iface=DBUS.INTERFACE_INTROSPECTABLE,
            method="Introspect",
        )

        reply = await self._conn.send_await_reply(message, timeout=10000)
        data = reply.expect_return_objects("s")[0]
        try:
            xml = ET.fromstring(data)
        except ET.ParseError as err:
            _LOGGER.error("Can't parse introspect data: %s", err)
            _LOGGER.debug("Introspect %s on %s", self.bus_name, self.object_path)
            raise DBusParseError() from err

        # Read available methods
        for interface in xml.findall("./interface"):
            interface_name = interface.get("name")

            # Methods
            for method in interface.findall("./method"):
                method_name = method.get("name")
                self.methods.add(f"{interface_name}.{method_name}")

            # Signals
            for signal in interface.findall("./signal"):
                signal_name = signal.get("name")
                self.signals.add(f"{interface_name}.{signal_name}")

    async def call_dbus(self, method: str, *args: list[Any]) -> str:
        """Call a dbus method."""

        _LOGGER.debug(
            "Call %s on %s (bus name %s)", method, self.object_path, self.bus_name
        )
        method_parts = method.split(".")
        request = dbussy.Message.new_method_call(
            destination=self.bus_name,
            path=self.object_path,
            iface=".".join(method_parts[:-1]),
            method=method_parts[-1],
        )

        for arg in args:
            _LOGGER.debug("...arg %s (type %s)", str(arg), type(arg))
            if isinstance(arg, bool):
                request.append_objects("b", arg)
            elif isinstance(arg, int):
                request.append_objects("i", arg)
            elif isinstance(arg, float):
                request.append_objects("d", arg)
            elif isinstance(arg, str):
                request.append_objects("s", arg)
            else:
                _LOGGER.warning("No explicit support for type %s, assuming string", type(arg))
                request.append_objects("s", str(arg))

        reply = await self._conn.send_await_reply(request)

        reply_object = _remove_dbus_signature(reply.all_objects)
        #_LOGGER.debug(reply_object)
        return reply_object

    async def get_properties(self, interface: str) -> dict[str, Any]:
        """Read all properties from interface."""
        _LOGGER.debug("Get all properties for interface %s.")
        try:
            dbussy.valid_interface(interface)
        except dbussy.DBusError as err:
            _LOGGER.error("Invalid interface %s", interface)
            raise DBusFatalError() from err

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
        _LOGGER.debug("wait_signal")
        conn = await dbussy.Connection.bus_get_async(DBUS.BUS_SYSTEM, private=True)
        conn.enable_receive_message({DBUS.MESSAGE_TYPE_SIGNAL})

        signal_parts = signal.split(".")
        interface = ".".join(signal_parts[:-1])
        member = signal_parts[-1]

        _LOGGER.debug("Use Bus AddMatch for interface %s, member %s", interface, member)
        conn.enable_receive_message({DBUS.MESSAGE_TYPE_SIGNAL})
        await conn.bus_add_match_async(f"type=signal,interface={interface},member={member}")

        try:
            while True:
                message = await conn.receive_message_async()
                _LOGGER.debug(
                    "Message received: %s.%s: %s",
                    message.interface,
                    message.member,
                    str(message.objects),   
                )
                if message.interface == interface and message.member == member:
                    return _remove_dbus_signature(message.objects)
        finally:
            conn.close()

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
