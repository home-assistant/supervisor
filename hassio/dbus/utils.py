"""Utils for D-Bus."""
import logging

from dbus_next import errors

from ..exceptions import DBusNotConnectedError, DBusError


_LOGGER = logging.getLogger(__name__)


def dbus_connected(method):
    """Wrapper for check if D-Bus is connected."""

    async def wrap_dbus(api, *args, **kwargs):
        """Check if D-Bus is connected before call a method."""
        if not api.is_connected:
            raise DBusNotConnectedError()
        try:
            return await method(api, *args, **kwargs)
        except errors.DBusError as err:
            _LOGGER.error("Error on dbus call: %s", err)
            raise DBusError() from None

    return wrap_dbus
