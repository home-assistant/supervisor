"""DBus implementation with glib."""
import asyncio
import logging
import json
import shlex
import re
from signal import SIGINT
import xml.etree.ElementTree as ET

from ..exceptions import DBusFatalError, DBusParseError

_LOGGER = logging.getLogger(__name__)

# Use to convert GVariant into json
RE_GVARIANT_TYPE = re.compile(
    r"(?:boolean|byte|int16|uint16|int32|uint32|handle|int64|uint64|double|"
    r"string|objectpath|signature) "
)
RE_GVARIANT_VARIANT = re.compile(
    r"(?<=(?: |{|\[))<((?:'|\").*?(?:'|\")|\d+(?:\.\d+)?)>(?=(?:|]|}|,))"
)
RE_GVARIANT_STRING = re.compile(r"(?<=(?: |{|\[|\())'(.*?)'(?=(?:|]|}|,|\)))")
RE_GVARIANT_TUPLE_O = re.compile(r"\"[^\"]*?\"|(\()")
RE_GVARIANT_TUPLE_C = re.compile(r"\"[^\"]*?\"|(,?\))")

RE_MONITOR_OUTPUT = re.compile(r".+?: (?P<signal>[^ ].+) (?P<data>.*)")

# Commands for dbus
INTROSPECT = "gdbus introspect --system --dest {bus} " "--object-path {object} --xml"
CALL = (
    "gdbus call --system --dest {bus} --object-path {object} "
    "--method {method} {args}"
)
MONITOR = "gdbus monitor --system --dest {bus}"

DBUS_METHOD_GETALL = "org.freedesktop.DBus.Properties.GetAll"


class DBus:
    """DBus handler."""

    def __init__(self, bus_name, object_path):
        """Initialize dbus object."""
        self.bus_name = bus_name
        self.object_path = object_path
        self.methods = set()
        self.signals = set()

    @staticmethod
    async def connect(bus_name, object_path):
        """Read object data."""
        self = DBus(bus_name, object_path)
        await self._init_proxy()  # pylint: disable=protected-access

        _LOGGER.info("Connect to dbus: %s - %s", bus_name, object_path)
        return self

    async def _init_proxy(self):
        """Read interface data."""
        command = shlex.split(
            INTROSPECT.format(bus=self.bus_name, object=self.object_path)
        )

        # Ask data
        _LOGGER.info("Introspect %s on %s", self.bus_name, self.object_path)
        data = await self._send(command)

        # Parse XML
        try:
            xml = ET.fromstring(data)
        except ET.ParseError as err:
            _LOGGER.error("Can't parse introspect data: %s", err)
            raise DBusParseError() from None

        # Read available methods
        _LOGGER.debug("data: %s", data)
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
    def parse_gvariant(raw):
        """Parse GVariant input to python."""
        raw = RE_GVARIANT_TYPE.sub("", raw)
        raw = RE_GVARIANT_VARIANT.sub(r"\1", raw)
        raw = RE_GVARIANT_STRING.sub(r'"\1"', raw)
        raw = RE_GVARIANT_TUPLE_O.sub(
            lambda x: x.group(0) if not x.group(1) else "[", raw
        )
        raw = RE_GVARIANT_TUPLE_C.sub(
            lambda x: x.group(0) if not x.group(1) else "]", raw
        )

        # No data
        if raw.startswith("[]"):
            return []

        try:
            return json.loads(raw)
        except json.JSONDecodeError as err:
            _LOGGER.error("Can't parse '%s': %s", raw, err)
            raise DBusParseError() from None

    @staticmethod
    def gvariant_args(args):
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
                gvariant += " {}".format(str(arg))

        return gvariant.lstrip()

    async def call_dbus(self, method, *args):
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
        _LOGGER.debug("Receive from %s: %s", method, data)
        return self.parse_gvariant(data)

    async def get_properties(self, interface):
        """Read all properties from interface."""
        try:
            return (await self.call_dbus(DBUS_METHOD_GETALL, interface))[0]
        except IndexError:
            _LOGGER.error("No attributes returned for %s", interface)
            raise DBusFatalError from None

    async def _send(self, command):
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
        if proc.returncode != 0:
            _LOGGER.error("DBus return error: %s", error)
            raise DBusFatalError()

        # End
        return data.decode()

    def attach_signals(self, filters=None):
        """Generate a signals wrapper."""
        return DBusSignalWrapper(self, filters)

    async def wait_signal(self, signal):
        """Wait for single event."""
        monitor = DBusSignalWrapper(self, [signal])
        async with monitor as signals:
            async for signal in signals:
                return signal

    def __getattr__(self, name):
        """Mapping to dbus method."""
        return getattr(DBusCallWrapper(self, self.bus_name), name)


class DBusCallWrapper:
    """Wrapper a DBus interface for a call."""

    def __init__(self, dbus, interface):
        """Initialize wrapper."""
        self.dbus = dbus
        self.interface = interface

    def __call__(self):
        """Should never be called."""
        _LOGGER.error("DBus method %s not exists!", self.interface)
        raise DBusFatalError()

    def __getattr__(self, name):
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

    def __init__(self, dbus, signals=None):
        """Initialize dbus signal wrapper."""
        self.dbus = dbus
        self._signals = signals
        self._proc = None

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
