"""Utils for D-Bus."""

from inspect import iscoroutinefunction

from ..exceptions import DBusNotConnectedError


async def noop():
    """Return a noop coroutine."""


def dbus_connected(method):
    """Wrap check if D-Bus is connected."""
    is_coroutine = iscoroutinefunction(method)

    def wrap_dbus(api, *args, **kwargs):
        """Check if D-Bus is connected before call a method."""
        # Only a coroutine can be replaced by a noop, a sync caller needs its value
        if api.is_shutdown and is_coroutine:
            return noop()
        if api.is_shutdown or api.dbus is None:
            raise DBusNotConnectedError
        return method(api, *args, **kwargs)

    return wrap_dbus
