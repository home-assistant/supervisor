"""Utils for D-Bus."""

from ..exceptions import DBusNotConnectedError


async def noop():
    """Return a noop coroutine."""


def dbus_connected(method):
    """Wrap check if D-Bus is connected."""

    def wrap_dbus(api, *args, **kwargs):
        """Check if D-Bus is connected before call a method."""
        if api.is_shutdown:
            return noop()
        if api.dbus is None:
            raise DBusNotConnectedError()
        return method(api, *args, **kwargs)

    return wrap_dbus
