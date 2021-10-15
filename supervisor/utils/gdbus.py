"""DBus implementation with glib."""
from __future__ import annotations

import asyncio
import json
import logging
import re
import shlex
from signal import SIGINT
from typing import Any
from dbus_next import Message, MessageType, BusType, InvalidIntrospectionError
from dbus_next.signature import Variant
from dbus_next.aio import MessageBus

import sentry_sdk

from . import clean_env
from ..exceptions import (
    DBusFatalError,
    DBusInterfaceError,
    DBusInterfaceMethodError,
    DBusNotConnectedError,
    DBusParseError,
    DBusProgramError,
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

# Use to convert GVariant into json
RE_GVARIANT_TYPE: re.Pattern[Any] = re.compile(
    r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(boolean|byte|int16|uint16|int32|uint32|handle|int64|uint64|double|"
    r"string|objectpath|signature|@[asviumodfy\{\}\(\)]+) "
)
RE_GVARIANT_VARIANT: re.Pattern[Any] = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(<|>)")
RE_GVARIANT_STRING_ESC: re.Pattern[Any] = re.compile(
    r"(?<=(?: |{|\[|\(|<))'[^']*?\"[^']*?'(?=(?:|]|}|,|\)|>))"
)
RE_GVARIANT_STRING: re.Pattern[Any] = re.compile(
    r"(?<=(?: |{|\[|\(|<))'(.*?)'(?=(?:|]|}|,|\)|>))"
)
RE_GVARIANT_BINARY: re.Pattern[Any] = re.compile(
    r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|\[byte (.*?)\]|\[(0x[0-9A-Za-z]{2}.*?)\]|<byte (.*?)>"
)
RE_GVARIANT_BINARY_STRING: re.Pattern[Any] = re.compile(
    r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|<?b\'(.*?)\'>?"
)
RE_GVARIANT_TUPLE_O: re.Pattern[Any] = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(\()")
RE_GVARIANT_TUPLE_C: re.Pattern[Any] = re.compile(
    r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(,?\))"
)

RE_BIN_STRING_OCT: re.Pattern[Any] = re.compile(r"\\\\(\d{3})")
RE_BIN_STRING_HEX: re.Pattern[Any] = re.compile(r"\\\\x([0-9A-Za-z]{2})")

RE_MONITOR_OUTPUT: re.Pattern[Any] = re.compile(
    r".+?: (?P<signal>[^\s].+?) (?P<data>.*)"
)

# Map GDBus to errors
MAP_GDBUS_ERROR: dict[str, Any] = {
    "GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown": DBusInterfaceError,
    "GDBus.Error:org.freedesktop.DBus.Error.Spawn.ChildExited": DBusFatalError,
    "No such file or directory": DBusNotConnectedError,
}

# Commands for dbus
CALL: str = "gdbus call --system --dest {bus} --object-path {object} --timeout 10 --method {method} {args}"
MONITOR: str = "gdbus monitor --system --dest {bus}"

DBUS_METHOD_GETALL: str = "org.freedesktop.DBus.Properties.GetAll"
DBUS_METHOD_SET: str = "org.freedesktop.DBus.Properties.Set"


def _convert_bytes(value: str) -> str:
    """Convert bytes to string or byte-array."""
    data: bytes = bytes(int(char, 0) for char in value.split(", "))
    return f"[{', '.join(str(char) for char in data)}]"


def _convert_bytes_string(value: str) -> str:
    """Convert bytes to string or byte-array."""
    data = RE_BIN_STRING_OCT.sub(lambda x: chr(int(x.group(1), 8)), value)
    data = RE_BIN_STRING_HEX.sub(lambda x: chr(int(f"0x{x.group(1)}", 0)), data)
    return f"[{', '.join(str(char) for char in list(char for char in data.encode()))}]"


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

    @staticmethod
    def parse_gvariant(raw: str) -> Any:
        """Parse GVariant input to python."""
        # Process first string
        json_raw = RE_GVARIANT_STRING_ESC.sub(
            lambda x: x.group(0).replace('"', '\\"'), raw
        )
        json_raw = RE_GVARIANT_STRING.sub(r'"\1"', json_raw)

        # Handle Bytes
        json_raw = RE_GVARIANT_BINARY.sub(
            lambda x: x.group(0)
            if not (x.group(1) or x.group(2) or x.group(3))
            else _convert_bytes(x.group(1) or x.group(2) or x.group(3)),
            json_raw,
        )
        json_raw = RE_GVARIANT_BINARY_STRING.sub(
            lambda x: x.group(0)
            if not x.group(1)
            else _convert_bytes_string(x.group(1)),
            json_raw,
        )

        # Remove complex type handling
        json_raw: str = RE_GVARIANT_TYPE.sub(
            lambda x: x.group(0) if not x.group(1) else "", json_raw
        )
        json_raw = RE_GVARIANT_VARIANT.sub(
            lambda x: x.group(0) if not x.group(1) else "", json_raw
        )
        json_raw = RE_GVARIANT_TUPLE_O.sub(
            lambda x: x.group(0) if not x.group(1) else "[", json_raw
        )
        json_raw = RE_GVARIANT_TUPLE_C.sub(
            lambda x: x.group(0) if not x.group(1) else "]", json_raw
        )

        # No data
        if json_raw.startswith("[]"):
            return []

        try:
            return json.loads(json_raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't parse '%s': '%s' - %s", json_raw, raw, err)
            sentry_sdk.capture_exception(err)
            raise DBusParseError() from err

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
            raise DBusFatalError(reply.body[0])

        # Parse and return data
        obj = _remove_dbus_signature(reply.body)
        return obj

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

    async def _send(self, command: list[str], silent=False) -> str:
        """Send command over dbus."""
        # Run command
        _LOGGER.debug("Send D-Bus command: %s", command)
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=clean_env(),
            )

            data, error = await proc.communicate()
        except OSError as err:
            _LOGGER.critical("D-Bus fatal error: %s", err)
            raise DBusFatalError() from err

        # Success?
        if proc.returncode == 0 or silent:
            return data.decode()

        # Filter error
        error = error.decode()
        for msg, exception in MAP_GDBUS_ERROR.items():
            if msg not in error:
                continue
            raise exception()

        # General
        _LOGGER.debug("D-Bus return: %s", error.strip())
        raise DBusProgramError(error.strip())

    def attach_signals(self, filters=None):
        """Generate a signals wrapper."""
        return DBusSignalWrapper(self, filters)

    async def wait_signal(self, signal):
        """Wait for single event."""
        monitor = DBusSignalWrapper(self, [signal])
        async with monitor as signals:
            async for signal in signals:
                return signal

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
    """Process Signals."""

    def __init__(self, dbus: DBus, signals: str | None = None):
        """Initialize dbus signal wrapper."""
        self.dbus: DBus = dbus
        self._signals: str | None = signals
        self._proc: asyncio.Process | None = None

    async def __aenter__(self):
        """Start monitor events."""
        _LOGGER.info("Starting dbus monitor on %s", self.dbus.bus_name)
        command = shlex.split(MONITOR.format(bus=self.dbus.bus_name))
        self._proc = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=clean_env(),
        )

        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        """Stop monitor events."""
        _LOGGER.info("Stopping dbus monitor on %s", self.dbus.bus_name)
        self._proc.send_signal(SIGINT)
        await self._proc.communicate()

    def __aiter__(self):
        """Start Iteratation."""
        return self

    async def __anext__(self):
        """Get next data."""
        if not self._proc:
            raise StopAsyncIteration() from None

        # Read signals
        while True:
            try:
                data = await self._proc.stdout.readline()
            except asyncio.TimeoutError:
                raise StopAsyncIteration() from None

            # Program close
            if not data:
                raise StopAsyncIteration() from None

            # Extract metadata
            match = RE_MONITOR_OUTPUT.match(data.decode())
            if not match:
                continue
            signal = match.group("signal")
            data = match.group("data")

            # Filter signals?
            if self._signals and signal not in self._signals:
                _LOGGER.debug("Skiping event %s - %s", signal, data)
                continue

            try:
                return self.dbus.parse_gvariant(data)
            except DBusParseError as err:
                raise StopAsyncIteration() from err
