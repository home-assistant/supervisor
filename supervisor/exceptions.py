"""Core Exceptions."""

from collections.abc import Callable


class HassioError(Exception):
    """Root exception."""

    def __init__(
        self,
        message: str | None = None,
        logger: Callable[..., None] | None = None,
    ) -> None:
        """Raise & log."""
        if logger is not None and message is not None:
            logger(message)

        # Init Base
        if message is not None:
            super().__init__(message)
        else:
            super().__init__()


class HassioNotSupportedError(HassioError):
    """Function is not supported."""


# JobManager


class JobException(HassioError):
    """Base job exception."""


class JobConditionException(JobException):
    """Exception happening for job conditions."""


class JobStartException(JobException):
    """Exception occurred starting a job on in current asyncio task."""


class JobNotFound(JobException):
    """Exception for job not found."""


class JobInvalidUpdate(JobException):
    """Exception for invalid update to a job."""


class JobGroupExecutionLimitExceeded(JobException):
    """Exception when job group execution limit exceeded."""


# HomeAssistant


class HomeAssistantError(HassioError):
    """Home Assistant exception."""


class HomeAssistantUpdateError(HomeAssistantError):
    """Error on update of a Home Assistant."""


class HomeAssistantCrashError(HomeAssistantError):
    """Error on crash of a Home Assistant startup."""


class HomeAssistantStartupTimeout(HomeAssistantCrashError):
    """Timeout waiting for Home Assistant successful startup."""


class HomeAssistantAPIError(HomeAssistantError):
    """Home Assistant API exception."""


class HomeAssistantAuthError(HomeAssistantAPIError):
    """Home Assistant Auth API exception."""


class HomeAssistantWSError(HomeAssistantAPIError):
    """Home Assistant websocket error."""


class HomeAssistantWSConnectionError(HomeAssistantWSError):
    """Raise when the WebSocket connection has an error."""


class HomeAssistantJobError(HomeAssistantError, JobException):
    """Raise on Home Assistant job error."""


# Supervisor


class SupervisorError(HassioError):
    """Supervisor error."""


class SupervisorUpdateError(SupervisorError):
    """Supervisor update error."""


class SupervisorAppArmorError(SupervisorError):
    """Supervisor AppArmor error."""


class SupervisorJobError(SupervisorError, JobException):
    """Raise on job errors."""


# HassOS


class HassOSError(HassioError):
    """HassOS exception."""


class HassOSUpdateError(HassOSError):
    """Error on update of a HassOS."""


class HassOSJobError(HassOSError, JobException):
    """Function not supported by HassOS."""


class HassOSDataDiskError(HassOSError):
    """Issues with the DataDisk feature from HAOS."""


class HassOSSlotNotFound(HassOSError):
    """Could not find boot slot."""


class HassOSSlotUpdateError(HassOSError):
    """Error while updating a slot via rauc."""


# All Plugins


class PluginError(HassioError):
    """Plugin error."""


class PluginJobError(PluginError, JobException):
    """Raise on job error with plugin."""


# HaCli


class CliError(PluginError):
    """HA cli exception."""


class CliUpdateError(CliError):
    """Error on update of a HA cli."""


class CliJobError(CliError, PluginJobError):
    """Raise on job error with cli plugin."""


# Observer


class ObserverError(PluginError):
    """General Observer exception."""


class ObserverUpdateError(ObserverError):
    """Error on update of a Observer."""


class ObserverJobError(ObserverError, PluginJobError):
    """Raise on job error with observer plugin."""


# Multicast


class MulticastError(PluginError):
    """Multicast exception."""


class MulticastUpdateError(MulticastError):
    """Error on update of a multicast."""


class MulticastJobError(MulticastError, PluginJobError):
    """Raise on job error with multicast plugin."""


# DNS


class CoreDNSError(PluginError):
    """CoreDNS exception."""


class CoreDNSUpdateError(CoreDNSError):
    """Error on update of a CoreDNS."""


class CoreDNSJobError(CoreDNSError, PluginJobError):
    """Raise on job error with dns plugin."""


# Audio


class AudioError(PluginError):
    """PulseAudio exception."""


class AudioUpdateError(AudioError):
    """Error on update of a Audio."""


class AudioJobError(AudioError, PluginJobError):
    """Raise on job error with audio plugin."""


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


class AuthListUsersError(HassioError):
    """Auth error if listing users failed."""


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


class HostLogError(HostError):
    """Internal error with host log."""


# API


class APIError(HassioError, RuntimeError):
    """API errors."""

    status = 400

    def __init__(
        self,
        message: str | None = None,
        logger: Callable[..., None] | None = None,
        job_id: str | None = None,
    ) -> None:
        """Raise & log, optionally with job."""
        super().__init__(message, logger)
        self.job_id = job_id


class APIForbidden(APIError):
    """API forbidden error."""

    status = 403


class APINotFound(APIError):
    """API not found error."""

    status = 404


class APIAddonNotInstalled(APIError):
    """Not installed addon requested at addons API."""


class APIDBMigrationInProgress(APIError):
    """Service is unavailable due to an offline DB migration is in progress."""

    status = 503


# Service / Discovery


class DiscoveryError(HassioError):
    """Discovery Errors."""


class ServicesError(HassioError):
    """Services Errors."""


# utils/dbus


class DBusError(HassioError):
    """D-Bus generic error."""


class DBusNotConnectedError(HostNotSupportedError):
    """D-Bus is not connected and call a method."""


class DBusServiceUnkownError(HassioNotSupportedError):
    """D-Bus service was not available."""


class DBusInterfaceError(HassioNotSupportedError):
    """D-Bus interface not connected."""


class DBusObjectError(HassioNotSupportedError):
    """D-Bus object not defined."""


class DBusInterfaceMethodError(DBusInterfaceError):
    """D-Bus method not defined or input does not match signature."""


class DBusInterfacePropertyError(DBusInterfaceError):
    """D-Bus property not defined or is read-only."""


class DBusInterfaceSignalError(DBusInterfaceError):
    """D-Bus signal not defined."""


class DBusParseError(DBusError):
    """D-Bus parse error."""


class DBusTimeoutError(DBusError):
    """D-Bus call timeout."""


class DBusTimedOutError(DBusError):
    """D-Bus call timed out (typically when systemd D-Bus service activation fail)."""


class DBusNoReplyError(DBusError):
    """D-Bus remote didn't reply/disconnected."""


class DBusFatalError(DBusError):
    """D-Bus call going wrong.

    Type field contains specific error from D-Bus for interface specific errors (like Systemd ones).
    """

    def __init__(
        self,
        message: str | None = None,
        logger: Callable[..., None] | None = None,
        type_: str | None = None,
    ) -> None:
        """Initialize object."""
        super().__init__(message, logger)
        self.type = type_


# dbus/systemd


class DBusSystemdNoSuchUnit(DBusError):
    """Systemd unit does not exist."""


# util/apparmor


class AppArmorError(HostAppArmorError):
    """General AppArmor error."""


class AppArmorFileError(AppArmorError):
    """AppArmor profile file error."""


class AppArmorInvalidError(AppArmorError):
    """AppArmor profile validate error."""


# util/boards


class BoardInvalidError(DBusObjectError):
    """System does not use the board specified."""


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


class PwnedSecret(PwnedError):
    """Pwned secrets found."""


class PwnedConnectivityError(PwnedError):
    """Connectivity errors while checking pwned passwords."""


# util/codenotary


class CodeNotaryError(HassioError):
    """Error general with CodeNotary."""


class CodeNotaryUntrusted(CodeNotaryError):
    """Error on untrusted content."""


class CodeNotaryBackendError(CodeNotaryError):
    """CodeNotary backend error happening."""


# util/whoami


class WhoamiError(HassioError):
    """Error while using whoami."""


class WhoamiSSLError(WhoamiError):
    """Error with the SSL certificate."""


class WhoamiConnectivityError(WhoamiError):
    """Connectivity errors while using whoami."""


# utils/systemd_journal


class SystemdJournalError(HassioError):
    """Error while processing systemd journal logs."""


class MalformedBinaryEntryError(SystemdJournalError):
    """Raised when binary entry in the journal isn't followed by a newline."""


# docker/api


class DockerError(HassioError):
    """Docker API/Transport errors."""


class DockerAPIError(DockerError):
    """Docker API error."""


class DockerRequestError(DockerError):
    """Dockerd OS issues."""


class DockerTrustError(DockerError):
    """Raise if images are not trusted."""


class DockerNotFound(DockerError):
    """Docker object don't Exists."""


class DockerJobError(DockerError, JobException):
    """Error executing docker job."""


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


class StoreGitCloneError(StoreGitError):
    """Raise if error occurred while cloning repository."""


class StoreNotFound(StoreError):
    """Raise if slug is not known."""


class StoreJobError(StoreError, JobException):
    """Raise on job error with git."""


class StoreInvalidAddonRepo(StoreError):
    """Raise on invalid addon repo."""


# Backup


class BackupError(HassioError):
    """Raise if an error during backup is happening."""


class HomeAssistantBackupError(BackupError, HomeAssistantError):
    """Raise if an error during Home Assistant Core backup is happening."""


class BackupInvalidError(BackupError):
    """Raise if backup or password provided is invalid."""


class BackupMountDownError(BackupError):
    """Raise if mount specified for backup is down."""


class BackupDataDiskBadMessageError(BackupError):
    """Raise if bad message error received from data disk during backup."""


class BackupJobError(BackupError, JobException):
    """Raise on Backup job error."""


class BackupFileNotFoundError(BackupError):
    """Raise if the backup file hasn't been found."""


class BackupPermissionError(BackupError):
    """Raise if we could not write the backup due to permission error."""


class BackupFileExistError(BackupError):
    """Raise if the backup file already exists."""


# Security


class SecurityError(HassioError):
    """Raise if an error during security checks are happening."""


class SecurityJobError(SecurityError, JobException):
    """Raise on Security job error."""


# Mount


class MountError(HassioError):
    """Raise on an error related to mounting/unmounting."""


class MountActivationError(MountError):
    """Raise on mount not reaching active state after mount/reload."""


class MountInvalidError(MountError):
    """Raise on invalid mount attempt."""


class MountNotFound(MountError):
    """Raise on mount not found."""


class MountJobError(MountError, JobException):
    """Raise on Mount job error."""


# Network


class NetworkInterfaceNotFound(HassioError):
    """Raise on network interface not found."""
