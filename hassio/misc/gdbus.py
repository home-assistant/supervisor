"""Dbus implementation with glib."""
import asyncio
import logging
import shlex

_LOGGER = logging.getLogger(__name__)

INTROSPECT = "gdbus introspect --system --dest {bus} --object-path {obj}"
CALL = ("gdbus call --system --dest {bus} --object-path {obj} "
        "--method {obj}.{method} {args}")


class DbusCallError(Exception):
    """Dbus call going wrong."""
    pass


class Dbus(object):
    """Dbus handler."""

    def __init__(self, loop, bus_name, object_path):
        """Initialize dbus object."""
        self.loop = loop
        self.bus_name = bus_name
        self.object_path = object_path

    async def _call_dbus(self, method, *args):
        """Call a dbus method."""
        command = shlex.split(CALL.format(
            bus=self.bus_name,
            obj=self.object_path,
            method=method,
            args=" ".join(args)))

        # Run command
        try:
            proc = await asyncio.create_subprocess_exec(
                *command,
                stdin=asyncio.subprocess.DEVNULL,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                loop=self.loop
            )

            data, _ = await proc.communicate()
        except OSError as err:
            _LOGGER.error("Can't send dbus command %s: %s", method, err)
            raise DbusCallError() from None

        # Success?
        if proc.returncode != 0:
            _LOGGER.info("Error %s.%s: %s", self.object_path, method, data)
            raise DbusCallError()

        # Parse and return data
        return self._gvariant(data)

    def __getattr__(self, name):
        """Mapping to dbus method."""
        def _method_wrapper(*args):
            """Wrap method.

            Return a coroutine
            """
            return self._call_dbus(name, *args)

        return _method_wrapper
