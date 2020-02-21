"""DBus implementation with glib."""
from __future__ import annotations

import asyncio
import logging
import json
import shlex
import re
from signal import SIGINT
from typing import Any, Dict, List, Optional, Set
import xml.etree.ElementTree as ET

from ..exceptions import (
    DBusFatalError,
    DBusParseError,
    DBusInterfaceError,
    DBusNotConnectedError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Use to convert GVariant into json
RE_GVARIANT_TYPE: re.Match = re.compile(
    r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(boolean|byte|int16|uint16|int32|uint32|handle|int64|uint64|double|"
    r"string|objectpath|signature|@[asviumodf\{\}]+) "
)
RE_GVARIANT_VARIANT: re.Match = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(<|>)")
RE_GVARIANT_STRING_ESC: re.Match = re.compile(
    r"(?<=(?: |{|\[|\(|<))'[^']*?\"[^']*?'(?=(?:|]|}|,|\)|>))"
)
RE_GVARIANT_STRING: re.Match = re.compile(
    r"(?<=(?: |{|\[|\(|<))'(.*?)'(?=(?:|]|}|,|\)|>))"
)
RE_GVARIANT_TUPLE_O: re.Match = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(\()")
RE_GVARIANT_TUPLE_C: re.Match = re.compile(r"\"[^\"\\]*(?:\\.[^\"\\]*)*\"|(,?\))")

RE_MONITOR_OUTPUT: re.Match = re.compile(r".+?: (?P<signal>[^ ].+) (?P<data>.*)")

# Map GDBus to errors
MAP_GDBUS_ERROR: Dict[str, Any] = {
    "GDBus.Error:org.freedesktop.DBus.Error.ServiceUnknown": DBusInterfaceError,
    "No such file or directory": DBusNotConnectedError,
}

# Commands for dbus
INTROSPECT: str = "gdbus introspect --system --dest {bus} " "--object-path {object} --xml"
CALL: str = (
    "gdbus call --system --dest {bus} --object-path {object} "
    "--method {method} {args}"
)
MONITOR: str = "gdbus monitor --system --dest {bus}"

DBUS_METHOD_GETALL: str = "org.freedesktop.DBus.Properties.GetAll"


class DBus:
    """DBus handler."""

    def __init__(self, bus_name: str, object_path: str) -> None:
        """Initialize dbus object."""
        self.bus_name: str = bus_name
        self.object_path: str = object_path
        self.methods: Set[str] = set()
        self.signals: Set[str] = set()

    @staticmethod
    async def connect(bus_name: str, object_path: str) -> DBus:
        """Read object data."""
        self = DBus(bus_name, object_path)

        # pylint: disable=protected-access
        await self._init_proxy()

        _LOGGER.info("Connect to dbus: %s - %s", bus_name, object_path)
        return self

    async def _init_proxy(self) -> None:
        """Read interface data."""
        command = shlex.split(
            INTROSPECT.format(bus=self.bus_name, object=self.object_path)
        )

        # Parse XML
        data = await self._send(command)
        try:
            xml = ET.fromstring(data)
        except ET.ParseError as err:
            _LOGGER.error("Can't parse introspect data: %s", err)
            _LOGGER.debug("Introspect %s on %s", self.bus_name, self.object_path)
            raise DBusParseError() from None

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

    @staticmethod
    def parse_gvariant(raw: str) -> Any:
        """Parse GVariant input to python."""
        # Process first string
        json_raw = RE_GVARIANT_STRING_ESC.sub(
            lambda x: x.group(0).replace('"', '\\"'), raw
        )
        json_raw = RE_GVARIANT_STRING.sub(r'"\1"', json_raw)

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
            _LOGGER.error("Can't parse '%s': %s", json_raw, err)
            _LOGGER.debug("GVariant data: '%s'", raw)
            raise DBusParseError() from None

    @staticmethod
    def gvariant_args(args: List[Any]) -> str:
        """Convert args into gvariant."""
        gvariant = ""
        for arg in args:
            if isinstance(arg, bool):
                gvariant += " {}".format(str(arg).lower())
            elif isinstance(arg, (int, float)):
                gvariant += f" {arg}"
            elif isinstance(arg, str):
                gvariant += f' "{arg}"'
            else:
                gvariant += f" {arg!s}"

        return gvariant.lstrip()

    async def call_dbus(self, method: str, *args: List[Any]) -> str:
        """Call a dbus method."""
        command = shlex.split(
            CALL.format(
                bus=self.bus_name,
                object=self.object_path,
                method=method,
                args=self.gvariant_args(args),
            )
        )

        # Run command
        _LOGGER.info("Call %s on %s", method, self.object_path)
        data = await self._send(command)

        # Parse and return data
        return self.parse_gvariant(data)

    async def get_properties(self, interface: str) -> Dict[str, Any]:
        """Read all properties from interface."""
        try:
            return (await self.call_dbus(DBUS_METHOD_GETALL, interface))[0]
        except IndexError:
            _LOGGER.error("No attributes returned for %s", interface)
            raise DBusFatalError from None

    async def _send(self, command: List[str]) -> str:
        """Send command over dbus."""
        # Run command
        _LOGGER.debug("Send dbus command: %s", command)
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            data, error = await proc.communicate()
        except OSError as err:
            _LOGGER.error("DBus fatal error: %s", err)
            raise DBusFatalError() from None

        # Success?
        if proc.returncode == 0:
            return data.decode()

        # Filter error
        error = error.decode()
        for msg, exception in MAP_GDBUS_ERROR.items():
            if msg not in error:
                continue
            raise exception()

        # General
        _LOGGER.error("DBus return error: %s", error)
        raise DBusFatalError()

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
        """Mapping to dbus method."""
        return getattr(DBusCallWrapper(self, self.bus_name), name)


class DBusCallWrapper:
    """Wrapper a DBus interface for a call."""

    def __init__(self, dbus: DBus, interface: str) -> None:
        """Initialize wrapper."""
        self.dbus: DBus = dbus
        self.interface: str = interface

    def __call__(self) -> None:
        """Should never be called."""
        _LOGGER.error("DBus method %s not exists!", self.interface)
        raise DBusFatalError()

    def __getattr__(self, name: str):
        """Mapping to dbus method."""
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

    def __init__(self, dbus: DBus, signals: Optional[str] = None):
        """Initialize dbus signal wrapper."""
        self.dbus: DBus = dbus
        self._signals: Optional[str] = signals
        self._proc: Optional[asyncio.Process] = None

    async def __aenter__(self):
        """Start monitor events."""
        _LOGGER.info("Start dbus monitor on %s", self.dbus.bus_name)
        command = shlex.split(MONITOR.format(bus=self.dbus.bus_name))
        self._proc = await asyncio.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.DEVNULL,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        return self

    async def __aexit__(self, exception_type, exception_value, traceback):
        """Stop monitor events."""
        _LOGGER.info("Stop dbus monitor on %s", self.dbus.bus_name)
        self._proc.send_signal(SIGINT)
        await self._proc.communicate()

    def __aiter__(self):
        """Start Iteratation."""
        return self

    async def __anext__(self):
        """Get next data."""
        if not self._proc:
            raise StopAsyncIteration()

        # Read signals
        while True:
            try:
                data = await self._proc.stdout.readline()
            except asyncio.TimeoutError:
                raise StopAsyncIteration() from None

            # Program close
            if not data:
                raise StopAsyncIteration()

            # Extract metadata
            match = RE_MONITOR_OUTPUT.match(data.decode())
            if not match:
                continue
            signal = match.group("signal")
            data = match.group("data")

            # Filter signals?
            if self._signals and signal not in self._signals:
                _LOGGER.debug("Skip event %s - %s", signal, data)
                continue

            try:
                return self.dbus.parse_gvariant(data)
            except DBusParseError:
                raise StopAsyncIteration() from None
