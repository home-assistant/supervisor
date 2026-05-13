"""Init file for Supervisor apps."""

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from contextlib import suppress
from datetime import datetime
import logging
from pathlib import Path
from typing import Any

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ..const import (
    ARCH_DEPRECATED,
    ATTR_APPARMOR,
    ATTR_ARCH,
    ATTR_AUDIO,
    ATTR_AUTH_API,
    ATTR_BACKUP_EXCLUDE,
    ATTR_BACKUP_POST,
    ATTR_BACKUP_PRE,
    ATTR_BOOT,
    ATTR_DESCRIPTON,
    ATTR_DEVICES,
    ATTR_DEVICETREE,
    ATTR_DISCOVERY,
    ATTR_DOCKER_API,
    ATTR_ENVIRONMENT,
    ATTR_FULL_ACCESS,
    ATTR_GPIO,
    ATTR_HASSIO_API,
    ATTR_HASSIO_ROLE,
    ATTR_HOMEASSISTANT,
    ATTR_HOMEASSISTANT_API,
    ATTR_HOST_DBUS,
    ATTR_HOST_IPC,
    ATTR_HOST_NETWORK,
    ATTR_HOST_PID,
    ATTR_HOST_UTS,
    ATTR_IMAGE,
    ATTR_INGRESS,
    ATTR_INGRESS_STREAM,
    ATTR_INIT,
    ATTR_JOURNALD,
    ATTR_KERNEL_MODULES,
    ATTR_LEGACY,
    ATTR_LOCATION,
    ATTR_MACHINE,
    ATTR_MAP,
    ATTR_NAME,
    ATTR_OPTIONS,
    ATTR_PANEL_ADMIN,
    ATTR_PANEL_ICON,
    ATTR_PANEL_TITLE,
    ATTR_PORTS,
    ATTR_PORTS_DESCRIPTION,
    ATTR_PRIVILEGED,
    ATTR_REALTIME,
    ATTR_REPOSITORY,
    ATTR_SCHEMA,
    ATTR_SERVICES,
    ATTR_SLUG,
    ATTR_STAGE,
    ATTR_STARTUP,
    ATTR_STDIN,
    ATTR_TIMEOUT,
    ATTR_TMPFS,
    ATTR_TRANSLATIONS,
    ATTR_TYPE,
    ATTR_UART,
    ATTR_UDEV,
    ATTR_ULIMITS,
    ATTR_URL,
    ATTR_USB,
    ATTR_VERSION,
    ATTR_VERSION_TIMESTAMP,
    ATTR_VIDEO,
    ATTR_WATCHDOG,
    ATTR_WEBUI,
    MACHINE_DEPRECATED,
    SECURITY_DEFAULT,
    SECURITY_DISABLE,
    SECURITY_PROFILE,
    AppBoot,
    AppBootConfig,
    AppStage,
    AppStartup,
    CpuArch,
)
from ..coresys import CoreSys
from ..docker.const import Capabilities
from ..exceptions import (
    AppFileReadError,
    AppNotSupportedArchitectureError,
    AppNotSupportedError,
    AppNotSupportedHomeAssistantVersionError,
    AppNotSupportedMachineTypeError,
    HassioArchNotFound,
)
from ..jobs.const import JOB_GROUP_ADDON
from ..jobs.job_group import JobGroup
from ..utils import version_is_new_enough
from ..utils.dt import utc_from_timestamp
from .configuration import FolderMapping
from .const import (
    ATTR_BACKUP,
    ATTR_BREAKING_VERSIONS,
    ATTR_PATH,
    ATTR_READ_ONLY,
    AppBackupMode,
    MappingType,
)
from .options import AppOptions, UiOptions
from .validate import RE_SERVICE

_LOGGER: logging.Logger = logging.getLogger(__name__)

Data = dict[str, Any]


class AppModel(JobGroup, ABC):
    """App Data layout."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        super().__init__(
            coresys, JOB_GROUP_ADDON.format_map(defaultdict(str, slug=slug)), slug
        )
        self.slug: str = slug
        self._path_icon_exists: bool = False
        self._path_logo_exists: bool = False
        self._path_changelog_exists: bool = False
        self._path_documentation_exists: bool = False

    @property
    @abstractmethod
    def data(self) -> Data:
        """Return app config/data."""

    @property
    @abstractmethod
    def is_installed(self) -> bool:
        """Return True if an app is installed."""

    @property
    @abstractmethod
    def is_detached(self) -> bool:
        """Return True if app is detached."""

    @property
    def available(self) -> bool:
        """Return True if this app is available on this platform."""
        return self._available(self.data)

    @property
    def options(self) -> dict[str, Any]:
        """Return options with local changes."""
        return self.data[ATTR_OPTIONS]

    @property
    def boot_config(self) -> AppBootConfig:
        """Return boot config."""
        return self.data[ATTR_BOOT]

    @property
    def boot(self) -> AppBoot:
        """Return boot config with prio local settings unless config is forced."""
        return AppBoot(self.data[ATTR_BOOT])

    @property
    def auto_update(self) -> bool | None:
        """Return if auto update is enable."""
        return None

    @property
    def name(self) -> str:
        """Return name of app."""
        return self.data[ATTR_NAME]

    @property
    def hostname(self) -> str:
        """Return slug/id of app."""
        return self.slug.replace("_", "-")

    @property
    def dns(self) -> list[str]:
        """Return list of DNS name for that app."""
        return []

    @property
    def timeout(self) -> int:
        """Return timeout of app for docker stop."""
        return self.data[ATTR_TIMEOUT]

    @property
    def uuid(self) -> str | None:
        """Return an API token for this app."""
        return None

    @property
    def supervisor_token(self) -> str | None:
        """Return access token for Supervisor API."""
        return None

    @property
    def ingress_token(self) -> str | None:
        """Return access token for Supervisor API."""
        return None

    @property
    def ingress_entry(self) -> str | None:
        """Return ingress external URL."""
        return None

    @property
    def description(self) -> str:
        """Return description of app."""
        return self.data[ATTR_DESCRIPTON]

    @property
    def repository(self) -> str:
        """Return repository of app."""
        return self.data[ATTR_REPOSITORY]

    @property
    def translations(self) -> dict:
        """Return app translations."""
        return self.data[ATTR_TRANSLATIONS]

    @property
    def latest_version(self) -> AwesomeVersion:
        """Return latest version of app."""
        return self.data[ATTR_VERSION]

    @property
    def latest_version_timestamp(self) -> datetime:
        """Return when latest version was first seen."""
        return utc_from_timestamp(self.data[ATTR_VERSION_TIMESTAMP])

    @property
    def version(self) -> AwesomeVersion:
        """Return version of app."""
        return self.data[ATTR_VERSION]

    @property
    def protected(self) -> bool:
        """Return if app is in protected mode."""
        return True

    @property
    def startup(self) -> AppStartup:
        """Return startup type of app."""
        return self.data[ATTR_STARTUP]

    @property
    def advanced(self) -> bool:
        """Return False; advanced mode is deprecated and no longer supported."""
        # Deprecated since Supervisor 2026.03.0; always returns False and can be
        # removed once that version is the minimum supported.
        return False

    @property
    def stage(self) -> AppStage:
        """Return stage mode of app."""
        return self.data[ATTR_STAGE]

    @property
    def services_role(self) -> dict[str, str]:
        """Return dict of services with rights."""
        services_list = self.data.get(ATTR_SERVICES, [])

        services = {}
        for data in services_list:
            service = RE_SERVICE.match(data)
            if service:
                services[service.group("service")] = service.group("rights")

        return services

    @property
    def discovery(self) -> list[str]:
        """Return list of discoverable components/platforms."""
        return self.data.get(ATTR_DISCOVERY, [])

    @property
    def ports_description(self) -> dict[str, str] | None:
        """Return descriptions of ports."""
        return self.data.get(ATTR_PORTS_DESCRIPTION)

    @property
    def ports(self) -> dict[str, int | None] | None:
        """Return ports of app."""
        return self.data.get(ATTR_PORTS)

    @property
    def ingress_url(self) -> str | None:
        """Return URL to ingress url."""
        return None

    @property
    def webui(self) -> str | None:
        """Return URL to webui or None."""
        return self.data.get(ATTR_WEBUI)

    @property
    def watchdog_url(self) -> str | None:
        """Return URL to for watchdog or None."""
        return self.data.get(ATTR_WATCHDOG)

    @property
    def ingress_port(self) -> int | None:
        """Return Ingress port."""
        return None

    @property
    def panel_icon(self) -> str:
        """Return panel icon for Ingress frame."""
        return self.data[ATTR_PANEL_ICON]

    @property
    def panel_title(self) -> str:
        """Return panel title for Ingress frame."""
        return self.data.get(ATTR_PANEL_TITLE, self.name)

    @property
    def panel_admin(self) -> bool:
        """Return if panel is only available for admin users."""
        return self.data[ATTR_PANEL_ADMIN]

    @property
    def host_network(self) -> bool:
        """Return True if app run on host network."""
        return self.data[ATTR_HOST_NETWORK]

    @property
    def host_pid(self) -> bool:
        """Return True if app run on host PID namespace."""
        return self.data[ATTR_HOST_PID]

    @property
    def host_ipc(self) -> bool:
        """Return True if app run on host IPC namespace."""
        return self.data[ATTR_HOST_IPC]

    @property
    def host_uts(self) -> bool:
        """Return True if app run on host UTS namespace."""
        return self.data[ATTR_HOST_UTS]

    @property
    def host_dbus(self) -> bool:
        """Return True if app run on host D-BUS."""
        return self.data[ATTR_HOST_DBUS]

    @property
    def static_devices(self) -> list[Path]:
        """Return static devices of app."""
        return [Path(node) for node in self.data.get(ATTR_DEVICES, [])]

    @property
    def environment(self) -> dict[str, str] | None:
        """Return environment of app."""
        return self.data.get(ATTR_ENVIRONMENT)

    @property
    def privileged(self) -> list[Capabilities]:
        """Return list of privilege."""
        return self.data.get(ATTR_PRIVILEGED, [])

    @property
    def apparmor(self) -> str:
        """Return True if AppArmor is enabled."""
        if not self.data.get(ATTR_APPARMOR):
            return SECURITY_DISABLE
        elif self.sys_host.apparmor.exists(self.slug):
            return SECURITY_PROFILE
        return SECURITY_DEFAULT

    @property
    def legacy(self) -> bool:
        """Return if the app don't support Home Assistant labels."""
        return self.data[ATTR_LEGACY]

    @property
    def access_docker_api(self) -> bool:
        """Return if the app need read-only Docker API access."""
        return self.data[ATTR_DOCKER_API]

    @property
    def access_hassio_api(self) -> bool:
        """Return True if the app access to Supervisor REASTful API."""
        return self.data[ATTR_HASSIO_API]

    @property
    def access_homeassistant_api(self) -> bool:
        """Return True if the app access to Home Assistant API proxy."""
        return self.data[ATTR_HOMEASSISTANT_API]

    @property
    def hassio_role(self) -> str:
        """Return Supervisor role for API."""
        return self.data[ATTR_HASSIO_ROLE]

    @property
    def backup_exclude(self) -> list[str]:
        """Return Exclude list for backup."""
        return self.data.get(ATTR_BACKUP_EXCLUDE, [])

    @property
    def backup_pre(self) -> str | None:
        """Return pre-backup command."""
        return self.data.get(ATTR_BACKUP_PRE)

    @property
    def backup_post(self) -> str | None:
        """Return post-backup command."""
        return self.data.get(ATTR_BACKUP_POST)

    @property
    def backup_mode(self) -> AppBackupMode:
        """Return if backup is hot/cold."""
        return self.data[ATTR_BACKUP]

    @property
    def default_init(self) -> bool:
        """Return True if the app have no own init."""
        return self.data[ATTR_INIT]

    @property
    def with_stdin(self) -> bool:
        """Return True if the app access use stdin input."""
        return self.data[ATTR_STDIN]

    @property
    def with_ingress(self) -> bool:
        """Return True if the app access support ingress."""
        return self.data[ATTR_INGRESS]

    @property
    def ingress_panel(self) -> bool | None:
        """Return True if the app access support ingress."""
        return None

    @property
    def ingress_stream(self) -> bool:
        """Return True if post requests to ingress should be streamed."""
        return self.data[ATTR_INGRESS_STREAM]

    @property
    def with_gpio(self) -> bool:
        """Return True if the app access to GPIO interface."""
        return self.data[ATTR_GPIO]

    @property
    def with_usb(self) -> bool:
        """Return True if the app need USB access."""
        return self.data[ATTR_USB]

    @property
    def with_uart(self) -> bool:
        """Return True if we should map all UART device."""
        return self.data[ATTR_UART]

    @property
    def with_udev(self) -> bool:
        """Return True if the app have his own udev."""
        return self.data[ATTR_UDEV]

    @property
    def ulimits(self) -> dict[str, Any]:
        """Return ulimits configuration."""
        return self.data[ATTR_ULIMITS]

    @property
    def with_kernel_modules(self) -> bool:
        """Return True if the app access to kernel modules."""
        return self.data[ATTR_KERNEL_MODULES]

    @property
    def with_realtime(self) -> bool:
        """Return True if the app need realtime schedule functions."""
        return self.data[ATTR_REALTIME]

    @property
    def with_full_access(self) -> bool:
        """Return True if the app want full access to hardware."""
        return self.data[ATTR_FULL_ACCESS]

    @property
    def with_devicetree(self) -> bool:
        """Return True if the app read access to devicetree."""
        return self.data[ATTR_DEVICETREE]

    @property
    def with_tmpfs(self) -> bool:
        """Return if tmp is in memory of app."""
        return self.data[ATTR_TMPFS]

    @property
    def access_auth_api(self) -> bool:
        """Return True if the app access to login/auth backend."""
        return self.data[ATTR_AUTH_API]

    @property
    def with_audio(self) -> bool:
        """Return True if the app access to audio."""
        return self.data[ATTR_AUDIO]

    @property
    def with_video(self) -> bool:
        """Return True if the app access to video."""
        return self.data[ATTR_VIDEO]

    @property
    def homeassistant_version(self) -> AwesomeVersion | None:
        """Return min Home Assistant version they needed by App."""
        return self.data.get(ATTR_HOMEASSISTANT)

    @property
    def url(self) -> str | None:
        """Return URL of app."""
        return self.data.get(ATTR_URL)

    @property
    def with_icon(self) -> bool:
        """Return True if an icon exists."""
        return self._path_icon_exists

    @property
    def with_logo(self) -> bool:
        """Return True if a logo exists."""
        return self._path_logo_exists

    @property
    def with_changelog(self) -> bool:
        """Return True if a changelog exists."""
        return self._path_changelog_exists

    @property
    def with_documentation(self) -> bool:
        """Return True if a documentation exists."""
        return self._path_documentation_exists

    @property
    def supported_arch(self) -> list[str]:
        """Return list of supported arch."""
        return self.data[ATTR_ARCH]

    @property
    def has_deprecated_arch(self) -> bool:
        """Return True if app includes deprecated architectures."""
        return any(arch in ARCH_DEPRECATED for arch in self.supported_arch)

    @property
    def has_supported_arch(self) -> bool:
        """Return True if app supports any architecture on this system."""
        return self.sys_arch.is_supported(self.supported_arch)

    @property
    def has_deprecated_machine(self) -> bool:
        """Return True if app includes deprecated machine entries."""
        return any(
            machine.lstrip("!") in MACHINE_DEPRECATED
            for machine in self.supported_machine
        )

    @property
    def has_supported_machine(self) -> bool:
        """Return True if app supports this machine."""
        if not (machine_types := self.supported_machine):
            return True

        return (
            f"!{self.sys_machine}" not in machine_types
            and self.sys_machine in machine_types
        )

    @property
    def supported_machine(self) -> list[str]:
        """Return list of supported machine."""
        return self.data.get(ATTR_MACHINE, [])

    @property
    def arch(self) -> CpuArch:
        """Return architecture to use for the app's image."""
        return self.sys_arch.match(self.data[ATTR_ARCH])

    @property
    def image(self) -> str | None:
        """Generate image name from data."""
        return self._image(self.data)

    @property
    def need_build(self) -> bool:
        """Return True if this  app need a local build."""
        return ATTR_IMAGE not in self.data

    @property
    def map_volumes(self) -> dict[MappingType, FolderMapping]:
        """Return a dict of {MappingType: FolderMapping} from app."""
        volumes = {}
        for volume in self.data[ATTR_MAP]:
            volumes[MappingType(volume[ATTR_TYPE])] = FolderMapping(
                volume.get(ATTR_PATH), volume[ATTR_READ_ONLY]
            )

        return volumes

    @property
    def path_location(self) -> Path:
        """Return path to this app."""
        return Path(self.data[ATTR_LOCATION])

    @property
    def path_icon(self) -> Path:
        """Return path to app icon."""
        return Path(self.path_location, "icon.png")

    @property
    def path_logo(self) -> Path:
        """Return path to app logo."""
        return Path(self.path_location, "logo.png")

    @property
    def path_changelog(self) -> Path:
        """Return path to app changelog."""
        return Path(self.path_location, "CHANGELOG.md")

    @property
    def path_documentation(self) -> Path:
        """Return path to app changelog."""
        return Path(self.path_location, "DOCS.md")

    @property
    def path_apparmor(self) -> Path:
        """Return path to custom AppArmor profile."""
        return Path(self.path_location, "apparmor.txt")

    @property
    def schema(self) -> AppOptions:
        """Return App options validation object."""
        raw_schema = self.data[ATTR_SCHEMA]
        if isinstance(raw_schema, bool):
            raw_schema = {}

        return AppOptions(self.coresys, raw_schema, self.name, self.slug)

    @property
    def schema_ui(self) -> list[dict[Any, Any]] | None:
        """Create a UI schema for app options."""
        raw_schema = self.data[ATTR_SCHEMA]

        if isinstance(raw_schema, bool):
            return None
        return UiOptions(self.coresys)(raw_schema)

    @property
    def with_journald(self) -> bool:
        """Return True if the app accesses the system journal."""
        return self.data[ATTR_JOURNALD]

    @property
    def signed(self) -> bool:
        """Currently no signing support."""
        return False

    @property
    def breaking_versions(self) -> list[AwesomeVersion]:
        """Return breaking versions of app."""
        return self.data[ATTR_BREAKING_VERSIONS]

    async def long_description(self) -> str | None:
        """Return README.md as long_description."""

        def read_readme() -> str | None:
            readme = Path(self.path_location, "README.md")

            # If readme not exists
            if not readme.exists():
                return None

            # Return data
            return readme.read_text(encoding="utf-8", errors="replace")

        try:
            return await self.sys_run_in_executor(read_readme)
        except OSError as err:
            self.sys_resolution.check_oserror(err)
            raise AppFileReadError(
                _LOGGER.error, app=self.slug, error=str(err)
            ) from err

    async def refresh_path_cache(self) -> None:
        """Refresh cache of existing paths."""

        def check_paths():
            self._path_icon_exists = self.path_icon.exists()
            self._path_logo_exists = self.path_logo.exists()
            self._path_changelog_exists = self.path_changelog.exists()
            self._path_documentation_exists = self.path_documentation.exists()

        try:
            await self.sys_run_in_executor(check_paths)
        except OSError as err:
            self.sys_resolution.check_oserror(err)
            raise AppFileReadError(
                _LOGGER.error, app=self.slug, error=str(err)
            ) from err

    def validate_availability(self) -> None:
        """Validate if app is available for current system."""
        return self._validate_availability(self.data, logger=_LOGGER.error)

    def __eq__(self, other: Any) -> bool:
        """Compare app objects."""
        if not isinstance(other, AppModel):
            return False
        return self.slug == other.slug

    def __hash__(self) -> int:
        """Hash for app objects."""
        return hash(self.slug)

    def _validate_availability(
        self, config, *, logger: Callable[..., None] | None = None
    ) -> None:
        """Validate if app is available for current system."""
        # Architecture
        if not self.sys_arch.is_supported(config[ATTR_ARCH]):
            raise AppNotSupportedArchitectureError(
                logger, slug=self.slug, architectures=config[ATTR_ARCH]
            )

        # Machine / Hardware
        machine = config.get(ATTR_MACHINE)
        if machine and (
            f"!{self.sys_machine}" in machine or self.sys_machine not in machine
        ):
            raise AppNotSupportedMachineTypeError(
                logger, slug=self.slug, machine_types=machine
            )

        # Home Assistant
        version: AwesomeVersion | None = config.get(ATTR_HOMEASSISTANT)
        with suppress(AwesomeVersionException, TypeError):
            if version and not version_is_new_enough(
                self.sys_homeassistant.version, version
            ):
                raise AppNotSupportedHomeAssistantVersionError(
                    logger, slug=self.slug, version=str(version)
                )

    def _available(self, config) -> bool:
        """Return True if this app is available on this platform."""
        try:
            self._validate_availability(config)
        except AppNotSupportedError:
            return False

        return True

    def _image(self, config) -> str:
        """Generate image name from data."""
        # Repository with Dockerhub images
        if ATTR_IMAGE in config:
            try:
                arch = self.sys_arch.match(config[ATTR_ARCH])
            except HassioArchNotFound:
                arch = self.sys_arch.default
            return config[ATTR_IMAGE].format(arch=arch)

        # local build
        arch = self.sys_arch.match(config[ATTR_ARCH])
        return f"{config[ATTR_REPOSITORY]}/{arch!s}-addon-{config[ATTR_SLUG]}"
