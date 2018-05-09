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


# Host

class HostError(HassioError):
    """Internal Host error."""
    pass


class HostNotSupportedError(HassioNotSupportedError):
    """Host function is not supprted."""
    pass


# utils/gdbus

class DBusError(HassioError):
    """DBus generic error."""
    pass


class DBusNotConnectedError(HostNotSupportedError):
    """DBus is not connected and call a method."""


class DBusFatalError(DBusError):
    """DBus call going wrong."""
    pass


class DBusParseError(DBusError):
    """DBus parse error."""
    pass
