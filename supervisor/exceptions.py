"""Core Exceptions."""

from collections.abc import Callable, Mapping
from typing import Any

MESSAGE_CHECK_SUPERVISOR_LOGS = (
    "Check supervisor logs for details (check with '{logs_command}')"
)
EXTRA_FIELDS_LOGS_COMMAND = {"logs_command": "ha supervisor logs"}


class HassioError(Exception):
    """Root exception."""

    error_key: str | None = None
    message_template: str | None = None
    extra_fields: dict[str, Any] | None = None

    def __init__(
        self, message: str | None = None, logger: Callable[..., None] | None = None
    ) -> None:
        """Raise & log."""
        if not message and self.message_template:
            message = (
                self.message_template.format(**self.extra_fields)
                if self.extra_fields
                else self.message_template
            )

        if logger is not None and message is not None:
            logger(message)

        # Init Base
        if message is not None:
            super().__init__(message)
        else:
            super().__init__()


class HassioNotSupportedError(HassioError):
    """Function is not supported."""


# API


class APIError(HassioError, RuntimeError):
    """API errors."""

    status = 400
    headers: Mapping[str, str] | None = None

    def __init__(
        self,
        message: str | None = None,
        logger: Callable[..., None] | None = None,
        *,
        headers: Mapping[str, str] | None = None,
        job_id: str | None = None,
    ) -> None:
        """Raise & log, optionally with job."""
        super().__init__(message, logger)
        self.headers = headers
        self.job_id = job_id


class APIUnauthorized(APIError):
    """API unauthorized error."""

    status = 401


class APIForbidden(APIError):
    """API forbidden error."""

    status = 403


class APINotFound(APIError):
    """API not found error."""

    status = 404


class APIGone(APIError):
    """API is no longer available."""

    status = 410


class APITooManyRequests(APIError):
    """API too many requests error."""

    status = 429


class APIInternalServerError(APIError):
    """API internal server error."""

    status = 500


class APIAddonNotInstalled(APIError):
    """Not installed addon requested at addons API."""


class APIDBMigrationInProgress(APIError):
    """Service is unavailable due to an offline DB migration is in progress."""

    status = 503


class APIUnknownSupervisorError(APIError):
    """Unknown error occurred within supervisor. Adds supervisor check logs rider to message template."""

    status = 500

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        job_id: str | None = None,
    ) -> None:
        """Initialize exception."""
        self.message_template = (
            f"{self.message_template}. {MESSAGE_CHECK_SUPERVISOR_LOGS}"
        )
        self.extra_fields = (self.extra_fields or {}) | EXTRA_FIELDS_LOGS_COMMAND
        super().__init__(None, logger, job_id=job_id)


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


class SupervisorUnknownError(SupervisorError, APIUnknownSupervisorError):
    """Raise when an unknown error occurs interacting with Supervisor or its container."""

    error_key = "supervisor_unknown_error"
    message_template = "An unknown error occurred with Supervisor"


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


class AddonConfigurationInvalidError(AddonConfigurationError, APIError):
    """Raise if invalid configuration provided for addon."""

    error_key = "addon_configuration_invalid_error"
    message_template = "Add-on {addon} has invalid options: {validation_error}"

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        addon: str,
        validation_error: str,
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon, "validation_error": validation_error}
        super().__init__(None, logger)


class AddonBootConfigCannotChangeError(AddonsError, APIError):
    """Raise if user attempts to change addon boot config when it can't be changed."""

    error_key = "addon_boot_config_cannot_change_error"
    message_template = (
        "Addon {addon} boot option is set to {boot_config} so it cannot be changed"
    )

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str, boot_config: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon, "boot_config": boot_config}
        super().__init__(None, logger)


class AddonNotRunningError(AddonsError, APIError):
    """Raise when an addon is not running."""

    error_key = "addon_not_running_error"
    message_template = "Add-on {addon} is not running"

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon}
        super().__init__(None, logger)


class AddonNotSupportedError(HassioNotSupportedError):
    """Addon doesn't support a function."""


class AddonNotSupportedArchitectureError(AddonNotSupportedError):
    """Addon does not support system due to architecture."""

    error_key = "addon_not_supported_architecture_error"
    message_template = "Add-on {slug} not supported on this platform, supported architectures: {architectures}"

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        slug: str,
        architectures: list[str],
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"slug": slug, "architectures": ", ".join(architectures)}
        super().__init__(None, logger)


class AddonNotSupportedMachineTypeError(AddonNotSupportedError):
    """Addon does not support system due to machine type."""

    error_key = "addon_not_supported_machine_type_error"
    message_template = "Add-on {slug} not supported on this machine, supported machine types: {machine_types}"

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        slug: str,
        machine_types: list[str],
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"slug": slug, "machine_types": ", ".join(machine_types)}
        super().__init__(None, logger)


class AddonNotSupportedHomeAssistantVersionError(AddonNotSupportedError):
    """Addon does not support system due to Home Assistant version."""

    error_key = "addon_not_supported_home_assistant_version_error"
    message_template = "Add-on {slug} not supported on this system, requires Home Assistant version {version} or greater"

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        slug: str,
        version: str,
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"slug": slug, "version": version}
        super().__init__(None, logger)


class AddonNotSupportedWriteStdinError(AddonNotSupportedError, APIError):
    """Addon does not support writing to stdin."""

    error_key = "addon_not_supported_write_stdin_error"
    message_template = "Add-on {addon} does not support writing to stdin"

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon}
        super().__init__(None, logger)


class AddonBuildDockerfileMissingError(AddonNotSupportedError, APIError):
    """Raise when addon build invalid because dockerfile is missing."""

    error_key = "addon_build_dockerfile_missing_error"
    message_template = (
        "Cannot build addon '{addon}' because dockerfile is missing. A repair "
        "using '{repair_command}' will fix this if the cause is data "
        "corruption. Otherwise please report this to the addon developer."
    )

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon, "repair_command": "ha supervisor repair"}
        super().__init__(None, logger)


class AddonBuildArchitectureNotSupportedError(AddonNotSupportedError, APIError):
    """Raise when addon cannot be built on system because it doesn't support its architecture."""

    error_key = "addon_build_architecture_not_supported_error"
    message_template = (
        "Cannot build addon '{addon}' because its supported architectures "
        "({addon_arches}) do not match the system supported architectures ({system_arches})"
    )

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        addon: str,
        addon_arch_list: list[str],
        system_arch_list: list[str],
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {
            "addon": addon,
            "addon_arches": ", ".join(addon_arch_list),
            "system_arches": ", ".join(system_arch_list),
        }
        super().__init__(None, logger)


class AddonUnknownError(AddonsError, APIUnknownSupervisorError):
    """Raise when unknown error occurs taking an action for an addon."""

    error_key = "addon_unknown_error"
    message_template = "An unknown error occurred with addon {addon}"

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon}
        super().__init__(logger)


class AddonBuildFailedUnknownError(AddonsError, APIUnknownSupervisorError):
    """Raise when the build failed for an addon due to an unknown error."""

    error_key = "addon_build_failed_unknown_error"
    message_template = (
        "An unknown error occurred while trying to build the image for addon {addon}"
    )

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon}
        super().__init__(logger)


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


# This one uses the check logs rider even though its not a 500 error because it
# is bad practice to return error specifics from a password reset API.
class AuthPasswordResetError(AuthError, APIError):
    """Auth error if password reset failed."""

    error_key = "auth_password_reset_error"
    message_template = (
        f"Unable to reset password for '{{user}}'. {MESSAGE_CHECK_SUPERVISOR_LOGS}"
    )

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        user: str,
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"user": user} | EXTRA_FIELDS_LOGS_COMMAND
        super().__init__(None, logger)


class AuthListUsersError(AuthError, APIUnknownSupervisorError):
    """Auth error if listing users failed."""

    error_key = "auth_list_users_error"
    message_template = "Can't request listing users on Home Assistant"


class AuthListUsersNoneResponseError(AuthError, APIInternalServerError):
    """Auth error if listing users returned invalid None response."""

    error_key = "auth_list_users_none_response_error"
    message_template = "Home Assistant returned invalid response of `{none}` instead of a list of users. Check Home Assistant logs for details (check with `{logs_command}`)"
    extra_fields = {"none": "None", "logs_command": "ha core logs"}

    def __init__(self, logger: Callable[..., None] | None = None) -> None:
        """Initialize exception."""
        super().__init__(None, logger)


class AuthInvalidNonStringValueError(AuthError, APIUnauthorized):
    """Auth error if something besides a string provided as username or password."""

    error_key = "auth_invalid_non_string_value_error"
    message_template = "Username and password must be strings"

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> None:
        """Initialize exception."""
        super().__init__(None, logger, headers=headers)


class AuthHomeAssistantAPIValidationError(AuthError, APIUnknownSupervisorError):
    """Error encountered trying to validate auth details via Home Assistant API."""

    error_key = "auth_home_assistant_api_validation_error"
    message_template = "Unable to validate authentication details with Home Assistant"


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


class DockerBuildError(DockerError):
    """Docker error during build."""


class DockerAPIError(DockerError):
    """Docker API error."""


class DockerRequestError(DockerError):
    """Dockerd OS issues."""


class DockerTrustError(DockerError):
    """Raise if images are not trusted."""


class DockerNotFound(DockerError):
    """Docker object don't Exists."""


class DockerLogOutOfOrder(DockerError):
    """Raise when log from docker action was out of order."""


class DockerNoSpaceOnDevice(DockerError):
    """Raise if a docker pull fails due to available space."""

    error_key = "docker_no_space_on_device"
    message_template = "No space left on disk"

    def __init__(self, logger: Callable[..., None] | None = None) -> None:
        """Raise & log."""
        super().__init__(None, logger=logger)


class DockerHubRateLimitExceeded(DockerError, APITooManyRequests):
    """Raise for docker hub rate limit exceeded error."""

    error_key = "dockerhub_rate_limit_exceeded"
    message_template = (
        "Your IP address has made too many requests to Docker Hub which activated a rate limit. "
        "For more details see {dockerhub_rate_limit_url}"
    )
    extra_fields = {
        "dockerhub_rate_limit_url": "https://www.home-assistant.io/more-info/dockerhub-rate-limit"
    }

    def __init__(self, logger: Callable[..., None] | None = None) -> None:
        """Raise & log."""
        super().__init__(None, logger=logger)


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


class StoreAddonNotFoundError(StoreError, APINotFound):
    """Raise if a requested addon is not in the store."""

    error_key = "store_addon_not_found_error"
    message_template = "Addon {addon} does not exist in the store"

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon}
        super().__init__(None, logger)


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


class BackupFileNotFoundError(BackupError, APINotFound):
    """Raise if the backup file hasn't been found."""


class BackupPermissionError(BackupError):
    """Raise if we could not write the backup due to permission error."""


class BackupFileExistError(BackupError):
    """Raise if the backup file already exists."""


class AddonBackupMetadataInvalidError(BackupError, APIError):
    """Raise if invalid metadata file provided for addon in backup."""

    error_key = "addon_backup_metadata_invalid_error"
    message_template = (
        "Metadata file for add-on {addon} in backup is invalid: {validation_error}"
    )

    def __init__(
        self,
        logger: Callable[..., None] | None = None,
        *,
        addon: str,
        validation_error: str,
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {"addon": addon, "validation_error": validation_error}
        super().__init__(None, logger)


class AddonPrePostBackupCommandReturnedError(BackupError, APIError):
    """Raise when addon's pre/post backup command returns an error."""

    error_key = "addon_pre_post_backup_command_returned_error"
    message_template = (
        "Pre-/Post backup command for add-on {addon} returned error code: "
        "{exit_code}. Please report this to the addon developer. Enable debug "
        "logging to capture complete command output using {debug_logging_command}"
    )

    def __init__(
        self, logger: Callable[..., None] | None = None, *, addon: str, exit_code: int
    ) -> None:
        """Initialize exception."""
        self.extra_fields = {
            "addon": addon,
            "exit_code": exit_code,
            "debug_logging_command": "ha supervisor options --logging debug",
        }
        super().__init__(None, logger)


class BackupRestoreUnknownError(BackupError, APIUnknownSupervisorError):
    """Raise when an unknown error occurs during backup or restore."""

    error_key = "backup_restore_unknown_error"
    message_template = "An unknown error occurred during backup/restore"


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
