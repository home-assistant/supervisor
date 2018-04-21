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
