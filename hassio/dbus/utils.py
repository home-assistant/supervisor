"""Utils for dbus."""

from ..exceptions import DBusNotConnectedError


def dbus_connected(method):
    """Wrapper for check if dbus is connected."""
    def wrap_dbus(api, *args, **kwargs):
        """Check if dbus is connected before call a method."""
        if api.dbus is None:
            raise DBusNotConnectedError()
        return method(api, *args, **kwargs)

    return wrap_dbus
