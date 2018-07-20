"""Core Exceptions."""
import asyncio

import aiohttp


class HassioError(Exception):
    """Root exception."""
    pass


class HassioNotSupportedError(HassioError):
    """Function is not supported."""
    pass


# HomeAssistant

class HomeAssistantError(HassioError):
    """Home Assistant exception."""
    pass


class HomeAssistantUpdateError(HomeAssistantError):
    """Error on update of a Home Assistant."""
    pass


class HomeAssistantAuthError(HomeAssistantError):
    """Home Assistant Auth API exception."""
    pass


class HomeAssistantAPIError(
        HomeAssistantAuthError, asyncio.TimeoutError, aiohttp.ClientError):
    """Home Assistant API exception."""
    pass


# HassOS

class HassOSError(HassioError):
    """HassOS exception."""
    pass


class HassOSUpdateError(HassOSError):
    """Error on update of a HassOS."""
    pass


class HassOSNotSupportedError(HassioNotSupportedError):
    """Function not supported by HassOS."""
    pass


# Updater

class HassioUpdaterError(HassioError):
    """Error on Updater."""
    pass


# Host

class HostError(HassioError):
    """Internal Host error."""
    pass


class HostNotSupportedError(HassioNotSupportedError):
    """Host function is not supprted."""
    pass


class HostServiceError(HostError):
    """Host service functions fails."""
    pass


class HostAppArmorError(HostError):
    """Host apparmor functions fails."""


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


# util/apparmor

class AppArmorError(HostAppArmorError):
    """General AppArmor error."""
    pass


class AppArmorFileError(AppArmorError):
    """AppArmor profile file error."""
    pass


class AppArmorInvalidError(AppArmorError):
    """AppArmor profile validate error."""
    pass
