"""Core Exceptions."""


class HassioError(Exception):
    """Root exception."""
    pass


class HassioInternalError(HassioError):
    """Internal Hass.io error they can't handle."""
    pass


class HassioNotSupportedError(HassioError):
    """Function is not supported."""
    pass


# utils/gdbus

class DBusError(HassioError):
    """DBus generic error."""
    pass


class DBusFatalError(DBusError):
    """DBus call going wrong."""
    pass


class DBusReturnError(DBusError):
    """DBus return error."""
    pass


class DBusParseError(DBusError):
    """DBus parse error."""
    pass
