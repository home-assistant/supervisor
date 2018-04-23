"""DBus implementation with glib."""
import asyncio
import logging
import shlex
import xml.etree.ElementTree as ET

from ..exceptions import DBusFatalError, DBusFatalError, DBusParseError

_LOGGER = logging.getLogger(__name__)

INTROSPECT = ("gdbus introspect --system --dest {bus} "
              "--object-path {obj} --xml")
CALL = ("gdbus call --system --dest {bus} --object-path {inf} "
        "--method {inf}.{method} {args}")


class DBus:
    """DBus handler."""

    def __init__(self, bus_name, object_path):
        """Initialize dbus object."""
        self.bus_name = bus_name
        self.object_path = object_path
        self.data = {}

    @staticmethod
    async def connect(bus_name, object_path):
        """Read object data."""
        self = DBus(bus_name, object_path)
        self._init_proxy()  # pylint: disable=protected-access

        _LOGGER.info("Connect to dbus: %s", bus_name)
        return self

    async def _init_proxy(self):
        """Read object data."""
        command = shlex.split(INTROSPECT.format(
            bus=self.bus_name,
            obj=self.object_path
        ))

        # Ask data
        _LOGGER.info("Introspect %s no %s", self.bus_name, self.object_path)
        data = await self._send(command)

        # Parse XML
        try:
            xml = ET.fromstring(data)
        except ET.ParseError as err:
            _LOGGER.error("Can't parse introspect data: %s", err)
            raise DBusParseError() from None

        # Read available methods
        for interface in xml.findall("/node/interface"):
            methods = set()
            for method in interface.findall("/method"):
                methods.add(method.get('name'))
            self.data[interface.get('name')] = methods

    @staticmethod
    def _gvariant(raw):
        """Parse GVariant input to python."""
        return raw

    async def call_dbus(self, interface, method, *args):
        """Call a dbus method."""
        command = shlex.split(CALL.format(
            bus=self.bus_name,
            inf=interface,
            method=method,
            args=" ".join(map(str, args))
        ))

        # Run command
        _LOGGER.info("Call %s no %s", method, interface)
        data = await self._send(command)

        # Parse and return data
        return self._gvariant(data)

    async def _send(self, command):
        """Send command over dbus."""
        # Run command
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL
            )

            data, _ = await proc.communicate()
        except OSError as err:
            _LOGGER.error("DBus fatal error: %s", err)
            raise DBusFatalError() from None

        # Success?
        if proc.returncode != 0:
            _LOGGER.error("DBus return error: %s", data)
            raise DBusFatalError()

        # End
        return data.decode()

    def __getattr__(self, interface):
        """Mapping to dbus method."""
        interface = f"{self.object_path}.{interface}"
        if interface not in self.data:
            raise AttributeError()

        return DBusCallWrapper(self, interface)


class DBusCallWrapper:
    """Wrapper a DBus interface for a call."""

    def __init__(self, dbus, interface):
        """Initialize wrapper."""
        self.dbus = dbus
        self.interface = interface

    def __getattr__(self, name):
        """Mapping to dbus method."""
        if name not in self.dbus.data[self.interface]:
            raise AttributeError()

        def _method_wrapper(*args):
            """Wrap method.

            Return a coroutine
            """
            return self.dbus.call_dbus(self.interface, self.name, *args)

        return _method_wrapper
