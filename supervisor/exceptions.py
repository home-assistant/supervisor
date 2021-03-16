"""Core Exceptions."""


from typing import Callable, Optional


class HassioError(Exception):
    """Root exception."""

    def __init__(
        self,
        message: Optional[str] = None,
        logger: Optional[Callable[..., None]] = None,
    ) -> None:
        """Raise & log."""
        if logger:
            logger(message)
        super().__init__(message)


class HassioNotSupportedError(HassioError):
    """Function is not supported."""


# JobManager


class JobException(HassioError):
    """Base job exception."""


# HomeAssistant


class HomeAssistantError(HassioError):
    """Home Assistant exception."""


class HomeAssistantUpdateError(HomeAssistantError):
    """Error on update of a Home Assistant."""


class HomeAssistantCrashError(HomeAssistantError):
    """Error on crash of a Home Assistant startup."""


class HomeAssistantAPIError(HomeAssistantError):
    """Home Assistant API exception."""


class HomeAssistantAuthError(HomeAssistantAPIError):
    """Home Assistant Auth API exception."""


class HomeAssistantWSError(HomeAssistantAPIError):
    """Home Assistant websocket error."""


class HomeAssistantWSNotSupported(HomeAssistantWSError):
    """Raise when WebSockets are not supported."""


class HomeAssistantJobError(HomeAssistantError, JobException):
    """Raise on Home Assistant job error."""


# Supervisor


class SupervisorError(HassioError):
    """Supervisor error."""


class SupervisorUpdateError(SupervisorError):
    """Supervisor update error."""


class SupervisorJobError(SupervisorError, JobException):
    """Raise on job errors."""


# HassOS


class HassOSError(HassioError):
    """HassOS exception."""


class HassOSUpdateError(HassOSError):
    """Error on update of a HassOS."""


class HassOSNotSupportedError(HassioNotSupportedError):
    """Function not supported by HassOS."""


# HaCli


class CliError(HassioError):
    """HA cli exception."""


class CliUpdateError(CliError):
    """Error on update of a HA cli."""


# Observer


class ObserverError(HassioError):
    """General Observer exception."""


class ObserverUpdateError(ObserverError):
    """Error on update of a Observer."""


# Multicast


class MulticastError(HassioError):
    """Multicast exception."""


class MulticastUpdateError(MulticastError):
    """Error on update of a multicast."""


# DNS


class CoreDNSError(HassioError):
    """CoreDNS exception."""


class CoreDNSUpdateError(CoreDNSError):
    """Error on update of a CoreDNS."""


# DNS


class AudioError(HassioError):
    """PulseAudio exception."""


class AudioUpdateError(AudioError):
    """Error on update of a Audio."""


# Addons


class AddonsError(HassioError):
    """Addons exception."""


class AddonConfigurationError(AddonsError):
    """Error with add-on configuration."""


class AddonsNotSupportedError(HassioNotSupportedError):
    """Addons don't support a function."""


class AddonsJobError(AddonsError, JobException):
    """Raise on job errors."""


# Arch


class HassioArchNotFound(HassioNotSupportedError):
    """No matches with exists arch."""


# Updater


class UpdaterError(HassioError):
    """Error on Updater."""


class UpdaterJobError(UpdaterError, JobException):
    """Raise on job error."""


# Auth


class AuthError(HassioError):
    """Auth errors."""


class AuthPasswordResetError(HassioError):
    """Auth error if password reset failed."""


# Host


class HostError(HassioError):
    """Internal Host error."""


class HostNotSupportedError(HassioNotSupportedError):
    """Host function is not supprted."""


class HostServiceError(HostError):
    """Host service functions failed."""


class HostAppArmorError(HostError):
    """Host apparmor functions failed."""


class HostNetworkError(HostError):
    """Error with host network."""


class HostNetworkNotFound(HostError):
    """Return if host interface is not found."""


# API


class APIError(HassioError, RuntimeError):
    """API errors."""


class APIForbidden(APIError):
    """API forbidden error."""


# Service / Discovery


class DiscoveryError(HassioError):
    """Discovery Errors."""


class ServicesError(HassioError):
    """Services Errors."""


# utils/gdbus


class DBusError(HassioError):
    """DBus generic error."""


class DBusNotConnectedError(HostNotSupportedError):
    """DBus is not connected and call a method."""


class DBusInterfaceError(HassioNotSupportedError):
    """DBus interface not connected."""


class DBusFatalError(DBusError):
    """DBus call going wrong."""


class DBusParseError(DBusError):
    """DBus parse error."""


class DBusProgramError(DBusError):
    """DBus application error."""


# util/apparmor


class AppArmorError(HostAppArmorError):
    """General AppArmor error."""


class AppArmorFileError(AppArmorError):
    """AppArmor profile file error."""


class AppArmorInvalidError(AppArmorError):
    """AppArmor profile validate error."""


# util/common


class ConfigurationFileError(HassioError):
    """Invalid JSON or YAML file."""


# util/json


class JsonFileError(ConfigurationFileError):
    """Invalid JSON file."""


# util/yaml


class YamlFileError(ConfigurationFileError):
    """Invalid YAML file."""


# util/pwned


class PwnedError(HassioError):
    """Errors while checking pwned passwords."""


class PwnedConnectivityError(PwnedError):
    """Connectivity errors while checking pwned passwords."""


# docker/api


class DockerError(HassioError):
    """Docker API/Transport errors."""


class DockerAPIError(DockerError):
    """Docker API error."""


class DockerRequestError(DockerError):
    """Dockerd OS issues."""


class DockerNotFound(DockerError):
    """Docker object don't Exists."""


# Hardware


class HardwareError(HassioError):
    """General Hardware Error on Supervisor."""


class HardwareNotFound(HardwareError):
    """Hardware path or device doesn't exist on the Host."""


class HardwareNotSupportedError(HassioNotSupportedError):
    """Raise if hardware function is not supported."""


# Pulse Audio


class PulseAudioError(HassioError):
    """Raise if an sound error is happening."""


# Resolution


class ResolutionError(HassioError):
    """Raise if an error is happning on resoltuion."""


class ResolutionCheckError(ResolutionError):
    """Raise when there are an issue managing checks."""


class ResolutionNotFound(ResolutionError):
    """Raise if suggestion/issue was not found."""


class ResolutionFixupError(HassioError):
    """Rasie if a fixup fails."""


class ResolutionFixupJobError(ResolutionFixupError, JobException):
    """Raise on job error."""


# Store


class StoreError(HassioError):
    """Raise if an error on store is happening."""


class StoreGitError(StoreError):
    """Raise if something on git is happening."""


class StoreNotFound(StoreError):
    """Raise if slug is not known."""


class StoreJobError(StoreError, JobException):
    """Raise on job error with git."""
