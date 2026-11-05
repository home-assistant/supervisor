"""Utils for D-Bus."""

from ..exceptions import DBusNotConnectedError


def dbus_connected(method):
    """Wrap check if D-Bus is connected."""

    def wrap_dbus(api, *args, **kwargs):
        """Check if D-Bus is connected before call a method."""
        if api.is_shutdown or api.dbus is None:
            raise DBusNotConnectedError
        return method(api, *args, **kwargs)

    return wrap_dbus


def dbus_signal_callback(method):
    """Wrap a signal callback that may still run once its object is shut down."""

    async def wrap_callback(api, *args, **kwargs) -> None:
        """Skip the callback after shutdown, including a shutdown mid-flight."""
        if api.is_shutdown:
            return
        try:
            await method(api, *args, **kwargs)
        except DBusNotConnectedError:
            if not api.is_shutdown:
                raise

    return wrap_callback
