"""Dbus implementation with glib."""
import asyncio
import logging
import shlex
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)

INTROSPECT = "gdbus introspect --system --dest {bus} --object-path {obj}"
CALL = ("gdbus call --system --dest {bus} --object-path {obj} "
        "--method {obj}.{method} {args}")


class DbusError(Exception):
    """Dbus generic error."""
    pass

class DbusFatalError(DbusError):
    """Dbus call going wrong."""
    pass

class DbusReturnError(DbusError):
    """Dbus return error."""
    pass


class Dbus(object):
    """Dbus handler."""

    def __init__(self, bus_name, object_path):
        """Initialize dbus object."""
        self.bus_name = bus_name
        self.object_path = object_path
        self.methods = []
    
    @staticmethod
    async def connect(bus_name, object_path):
        """Read object data."""
        self = Dbus(bus_name, object_path)
        self._init_proxy()

        _LOGGER.info("Connect to dbus: %s", bus_name)
        return self
        
    async def _init_proxy(self):
        """Read object data."""
    
    @staticmethod
    def _gvariant(raw):
        """Parse GVariant input to python."""
        return raw

    async def _call_dbus(self, method, *args):
        """Call a dbus method."""
        command = shlex.split(CALL.format(
            bus=self.bus_name,
            obj=self.object_path,
            method=method,
            args=" ".join(map(str, args))
        ))

        # Run command
        try:
            data = await self._send(command)
        except DBusError:
            _LOGGER.error(
                "Dbus fails with %s on %s", method, self.object_path)
            raise

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
            raise DbusFatalError() from None

        # Success?
        if proc.returncode != 0:
            raise DbusReturnError()

        # End
        return data.decode()

    def __getattr__(self, name):
        """Mapping to dbus method."""
        if name not in self.methods:
            raise AttributeError()

        def _method_wrapper(*args):
            """Wrap method.

            Return a coroutine
            """
            return self._call_dbus(name, *args)

        return _method_wrapper
