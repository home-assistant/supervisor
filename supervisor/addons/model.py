"""Init file for Supervisor add-ons."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Awaitable, Dict, List, Optional

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ..const import (
    ATTR_ADVANCED,
    ATTR_APPARMOR,
    ATTR_ARCH,
    ATTR_AUDIO,
    ATTR_AUTH_API,
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
    ATTR_IMAGE,
    ATTR_INGRESS,
    ATTR_INIT,
    ATTR_JOURNALD,
    ATTR_KERNEL_MODULES,
    ATTR_LEGACY,
    ATTR_LOCATON,
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
    ATTR_SNAPSHOT_EXCLUDE,
    ATTR_SNAPSHOT_POST,
    ATTR_SNAPSHOT_PRE,
    ATTR_STAGE,
    ATTR_STARTUP,
    ATTR_STDIN,
    ATTR_TIMEOUT,
    ATTR_TMPFS,
    ATTR_TRANSLATIONS,
    ATTR_UART,
    ATTR_UDEV,
    ATTR_URL,
    ATTR_USB,
    ATTR_VERSION,
    ATTR_VIDEO,
    ATTR_WATCHDOG,
    ATTR_WEBUI,
    SECURITY_DEFAULT,
    SECURITY_DISABLE,
    SECURITY_PROFILE,
    AddonBoot,
    AddonStage,
    AddonStartup,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.const import Capabilities
from .options import AddonOptions, UiOptions
from .validate import RE_SERVICE, RE_VOLUME

Data = Dict[str, Any]


class AddonModel(CoreSysAttributes, ABC):
    """Add-on Data layout."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.slug: str = slug

    @property
    @abstractmethod
    def data(self) -> Data:
        """Return add-on config/data."""

    @property
    @abstractmethod
    def is_installed(self) -> bool:
        """Return True if an add-on is installed."""

    @property
    @abstractmethod
    def is_detached(self) -> bool:
        """Return True if add-on is detached."""

    @property
    def available(self) -> bool:
        """Return True if this add-on is available on this platform."""
        return self._available(self.data)

    @property
    def options(self) -> Dict[str, Any]:
        """Return options with local changes."""
        return self.data[ATTR_OPTIONS]

    @property
    def boot(self) -> AddonBoot:
        """Return boot config with prio local settings."""
        return self.data[ATTR_BOOT]

    @property
    def auto_update(self) -> Optional[bool]:
        """Return if auto update is enable."""
        return None

    @property
    def name(self) -> str:
        """Return name of add-on."""
        return self.data[ATTR_NAME]

    @property
    def hostname(self) -> str:
        """Return slug/id of add-on."""
        return self.slug.replace("_", "-")

    @property
    def dns(self) -> List[str]:
        """Return list of DNS name for that add-on."""
        return []

    @property
    def timeout(self) -> int:
        """Return timeout of addon for docker stop."""
        return self.data[ATTR_TIMEOUT]

    @property
    def uuid(self) -> Optional[str]:
        """Return an API token for this add-on."""
        return None

    @property
    def supervisor_token(self) -> Optional[str]:
        """Return access token for Supervisor API."""
        return None

    @property
    def ingress_token(self) -> Optional[str]:
        """Return access token for Supervisor API."""
        return None

    @property
    def ingress_entry(self) -> Optional[str]:
        """Return ingress external URL."""
        return None

    @property
    def description(self) -> str:
        """Return description of add-on."""
        return self.data[ATTR_DESCRIPTON]

    @property
    def long_description(self) -> Optional[str]:
        """Return README.md as long_description."""
        readme = Path(self.path_location, "README.md")

        # If readme not exists
        if not readme.exists():
            return None

        # Return data
        with readme.open("r") as readme_file:
            return readme_file.read()

    @property
    def repository(self) -> str:
        """Return repository of add-on."""
        return self.data[ATTR_REPOSITORY]

    @property
    def translations(self) -> dict:
        """Return add-on translations."""
        return self.data[ATTR_TRANSLATIONS]

    @property
    def latest_version(self) -> AwesomeVersion:
        """Return latest version of add-on."""
        return self.data[ATTR_VERSION]

    @property
    def version(self) -> AwesomeVersion:
        """Return version of add-on."""
        return self.data[ATTR_VERSION]

    @property
    def protected(self) -> bool:
        """Return if add-on is in protected mode."""
        return True

    @property
    def startup(self) -> AddonStartup:
        """Return startup type of add-on."""
        return self.data[ATTR_STARTUP]

    @property
    def advanced(self) -> bool:
        """Return advanced mode of add-on."""
        return self.data[ATTR_ADVANCED]

    @property
    def stage(self) -> AddonStage:
        """Return stage mode of add-on."""
        return self.data[ATTR_STAGE]

    @property
    def services_role(self) -> Dict[str, str]:
        """Return dict of services with rights."""
        services_list = self.data.get(ATTR_SERVICES, [])

        services = {}
        for data in services_list:
            service = RE_SERVICE.match(data)
            if service:
                services[service.group("service")] = service.group("rights")

        return services

    @property
    def discovery(self) -> List[str]:
        """Return list of discoverable components/platforms."""
        return self.data.get(ATTR_DISCOVERY, [])

    @property
    def ports_description(self) -> Optional[Dict[str, str]]:
        """Return descriptions of ports."""
        return self.data.get(ATTR_PORTS_DESCRIPTION)

    @property
    def ports(self) -> Optional[Dict[str, Optional[int]]]:
        """Return ports of add-on."""
        return self.data.get(ATTR_PORTS)

    @property
    def ingress_url(self) -> Optional[str]:
        """Return URL to ingress url."""
        return None

    @property
    def webui(self) -> Optional[str]:
        """Return URL to webui or None."""
        return self.data.get(ATTR_WEBUI)

    @property
    def watchdog(self) -> Optional[str]:
        """Return URL to for watchdog or None."""
        return self.data.get(ATTR_WATCHDOG)

    @property
    def ingress_port(self) -> Optional[int]:
        """Return Ingress port."""
        return None

    @property
    def panel_icon(self) -> str:
        """Return panel icon for Ingress frame."""
        return self.data[ATTR_PANEL_ICON]

    @property
    def panel_title(self) -> str:
        """Return panel icon for Ingress frame."""
        return self.data.get(ATTR_PANEL_TITLE, self.name)

    @property
    def panel_admin(self) -> str:
        """Return panel icon for Ingress frame."""
        return self.data[ATTR_PANEL_ADMIN]

    @property
    def host_network(self) -> bool:
        """Return True if add-on run on host network."""
        return self.data[ATTR_HOST_NETWORK]

    @property
    def host_pid(self) -> bool:
        """Return True if add-on run on host PID namespace."""
        return self.data[ATTR_HOST_PID]

    @property
    def host_ipc(self) -> bool:
        """Return True if add-on run on host IPC namespace."""
        return self.data[ATTR_HOST_IPC]

    @property
    def host_dbus(self) -> bool:
        """Return True if add-on run on host D-BUS."""
        return self.data[ATTR_HOST_DBUS]

    @property
    def static_devices(self) -> List[Path]:
        """Return static devices of add-on."""
        return [Path(node) for node in self.data.get(ATTR_DEVICES, [])]

    @property
    def environment(self) -> Optional[Dict[str, str]]:
        """Return environment of add-on."""
        return self.data.get(ATTR_ENVIRONMENT)

    @property
    def privileged(self) -> List[Capabilities]:
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
        """Return if the add-on don't support Home Assistant labels."""
        return self.data[ATTR_LEGACY]

    @property
    def access_docker_api(self) -> bool:
        """Return if the add-on need read-only Docker API access."""
        return self.data[ATTR_DOCKER_API]

    @property
    def access_hassio_api(self) -> bool:
        """Return True if the add-on access to Supervisor REASTful API."""
        return self.data[ATTR_HASSIO_API]

    @property
    def access_homeassistant_api(self) -> bool:
        """Return True if the add-on access to Home Assistant API proxy."""
        return self.data[ATTR_HOMEASSISTANT_API]

    @property
    def hassio_role(self) -> str:
        """Return Supervisor role for API."""
        return self.data[ATTR_HASSIO_ROLE]

    @property
    def snapshot_exclude(self) -> List[str]:
        """Return Exclude list for snapshot."""
        return self.data.get(ATTR_SNAPSHOT_EXCLUDE, [])

    @property
    def snapshot_pre(self) -> Optional[str]:
        """Return pre-snapshot command."""
        return self.data.get(ATTR_SNAPSHOT_PRE)

    @property
    def snapshot_post(self) -> Optional[str]:
        """Return post-snapshot command."""
        return self.data.get(ATTR_SNAPSHOT_POST)

    @property
    def default_init(self) -> bool:
        """Return True if the add-on have no own init."""
        return self.data[ATTR_INIT]

    @property
    def with_stdin(self) -> bool:
        """Return True if the add-on access use stdin input."""
        return self.data[ATTR_STDIN]

    @property
    def with_ingress(self) -> bool:
        """Return True if the add-on access support ingress."""
        return self.data[ATTR_INGRESS]

    @property
    def ingress_panel(self) -> Optional[bool]:
        """Return True if the add-on access support ingress."""
        return None

    @property
    def with_gpio(self) -> bool:
        """Return True if the add-on access to GPIO interface."""
        return self.data[ATTR_GPIO]

    @property
    def with_usb(self) -> bool:
        """Return True if the add-on need USB access."""
        return self.data[ATTR_USB]

    @property
    def with_uart(self) -> bool:
        """Return True if we should map all UART device."""
        return self.data[ATTR_UART]

    @property
    def with_udev(self) -> bool:
        """Return True if the add-on have his own udev."""
        return self.data[ATTR_UDEV]

    @property
    def with_kernel_modules(self) -> bool:
        """Return True if the add-on access to kernel modules."""
        return self.data[ATTR_KERNEL_MODULES]

    @property
    def with_realtime(self) -> bool:
        """Return True if the add-on need realtime schedule functions."""
        return self.data[ATTR_REALTIME]

    @property
    def with_full_access(self) -> bool:
        """Return True if the add-on want full access to hardware."""
        return self.data[ATTR_FULL_ACCESS]

    @property
    def with_devicetree(self) -> bool:
        """Return True if the add-on read access to devicetree."""
        return self.data[ATTR_DEVICETREE]

    @property
    def with_tmpfs(self) -> Optional[str]:
        """Return if tmp is in memory of add-on."""
        return self.data[ATTR_TMPFS]

    @property
    def access_auth_api(self) -> bool:
        """Return True if the add-on access to login/auth backend."""
        return self.data[ATTR_AUTH_API]

    @property
    def with_audio(self) -> bool:
        """Return True if the add-on access to audio."""
        return self.data[ATTR_AUDIO]

    @property
    def with_video(self) -> bool:
        """Return True if the add-on access to video."""
        return self.data[ATTR_VIDEO]

    @property
    def homeassistant_version(self) -> Optional[str]:
        """Return min Home Assistant version they needed by Add-on."""
        return self.data.get(ATTR_HOMEASSISTANT)

    @property
    def url(self) -> Optional[str]:
        """Return URL of add-on."""
        return self.data.get(ATTR_URL)

    @property
    def with_icon(self) -> bool:
        """Return True if an icon exists."""
        return self.path_icon.exists()

    @property
    def with_logo(self) -> bool:
        """Return True if a logo exists."""
        return self.path_logo.exists()

    @property
    def with_changelog(self) -> bool:
        """Return True if a changelog exists."""
        return self.path_changelog.exists()

    @property
    def with_documentation(self) -> bool:
        """Return True if a documentation exists."""
        return self.path_documentation.exists()

    @property
    def supported_arch(self) -> List[str]:
        """Return list of supported arch."""
        return self.data[ATTR_ARCH]

    @property
    def supported_machine(self) -> List[str]:
        """Return list of supported machine."""
        return self.data.get(ATTR_MACHINE, [])

    @property
    def image(self) -> Optional[str]:
        """Generate image name from data."""
        return self._image(self.data)

    @property
    def need_build(self) -> bool:
        """Return True if this  add-on need a local build."""
        return ATTR_IMAGE not in self.data

    @property
    def map_volumes(self) -> Dict[str, str]:
        """Return a dict of {volume: policy} from add-on."""
        volumes = {}
        for volume in self.data[ATTR_MAP]:
            result = RE_VOLUME.match(volume)
            if not result:
                continue
            volumes[result.group(1)] = result.group(2) or "ro"

        return volumes

    @property
    def path_location(self) -> Path:
        """Return path to this add-on."""
        return Path(self.data[ATTR_LOCATON])

    @property
    def path_icon(self) -> Path:
        """Return path to add-on icon."""
        return Path(self.path_location, "icon.png")

    @property
    def path_logo(self) -> Path:
        """Return path to add-on logo."""
        return Path(self.path_location, "logo.png")

    @property
    def path_changelog(self) -> Path:
        """Return path to add-on changelog."""
        return Path(self.path_location, "CHANGELOG.md")

    @property
    def path_documentation(self) -> Path:
        """Return path to add-on changelog."""
        return Path(self.path_location, "DOCS.md")

    @property
    def path_apparmor(self) -> Path:
        """Return path to custom AppArmor profile."""
        return Path(self.path_location, "apparmor.txt")

    @property
    def schema(self) -> AddonOptions:
        """Return Addon options validation object."""
        raw_schema = self.data[ATTR_SCHEMA]
        if isinstance(raw_schema, bool):
            raw_schema = {}

        return AddonOptions(self.coresys, raw_schema, self.name, self.slug)

    @property
    def schema_ui(self) -> Optional[List[Dict[any, any]]]:
        """Create a UI schema for add-on options."""
        raw_schema = self.data[ATTR_SCHEMA]

        if isinstance(raw_schema, bool):
            return None
        return UiOptions(self.coresys)(raw_schema)

    @property
    def with_journald(self) -> bool:
        """Return True if the add-on accesses the system journal."""
        return self.data[ATTR_JOURNALD]

    def __eq__(self, other):
        """Compaired add-on objects."""
        if not isinstance(other, AddonModel):
            return False
        return self.slug == other.slug

    def _available(self, config) -> bool:
        """Return True if this add-on is available on this platform."""
        # Architecture
        if not self.sys_arch.is_supported(config[ATTR_ARCH]):
            return False

        # Machine / Hardware
        machine = config.get(ATTR_MACHINE)
        if machine and f"!{self.sys_machine}" in machine:
            return False
        elif machine and self.sys_machine not in machine:
            return False

        # Home Assistant
        version: Optional[AwesomeVersion] = config.get(ATTR_HOMEASSISTANT)
        try:
            return self.sys_homeassistant.version >= version
        except (AwesomeVersionException, TypeError):
            return True

    def _image(self, config) -> str:
        """Generate image name from data."""
        # Repository with Dockerhub images
        if ATTR_IMAGE in config:
            arch = self.sys_arch.match(config[ATTR_ARCH])
            return config[ATTR_IMAGE].format(arch=arch)

        # local build
        return f"{config[ATTR_REPOSITORY]}/{self.sys_arch.default}-addon-{config[ATTR_SLUG]}"

    def install(self) -> Awaitable[None]:
        """Install this add-on."""
        return self.sys_addons.install(self.slug)

    def uninstall(self) -> Awaitable[None]:
        """Uninstall this add-on."""
        return self.sys_addons.uninstall(self.slug)

    def update(self) -> Awaitable[None]:
        """Update this add-on."""
        return self.sys_addons.update(self.slug)

    def rebuild(self) -> Awaitable[None]:
        """Rebuild this add-on."""
        return self.sys_addons.rebuild(self.slug)
