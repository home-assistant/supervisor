"""Init file for Supervisor add-ons."""

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
from copy import deepcopy
from datetime import datetime
import errno
from functools import partial
from ipaddress import IPv4Address
import logging
from pathlib import Path, PurePath
import re
import secrets
import shutil
import tarfile
from tempfile import TemporaryDirectory
from typing import Any, Final

import aiohttp
from awesomeversion import AwesomeVersion, AwesomeVersionCompareException
from deepmerge import Merger
from securetar import AddFileError, atomic_contents_add, secure_path
import voluptuous as vol
from voluptuous.humanize import humanize_error

from supervisor.utils.dt import utc_from_timestamp

from ..bus import EventListener
from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_AUTO_UPDATE,
    ATTR_BOOT,
    ATTR_IMAGE,
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PANEL,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_TOKEN,
    ATTR_NETWORK,
    ATTR_OPTIONS,
    ATTR_PORTS,
    ATTR_PROTECTED,
    ATTR_SCHEMA,
    ATTR_SLUG,
    ATTR_STATE,
    ATTR_SYSTEM,
    ATTR_SYSTEM_MANAGED,
    ATTR_SYSTEM_MANAGED_CONFIG_ENTRY,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_VERSION_TIMESTAMP,
    ATTR_WATCHDOG,
    DNS_SUFFIX,
    AddonBoot,
    AddonBootConfig,
    AddonStartup,
    AddonState,
    BusEvent,
)
from ..coresys import CoreSys
from ..docker.addon import DockerAddon
from ..docker.const import ContainerState
from ..docker.monitor import DockerContainerStateEvent
from ..docker.stats import DockerStats
from ..exceptions import (
    AddonConfigurationError,
    AddonsError,
    AddonsJobError,
    AddonsNotSupportedError,
    ConfigurationFileError,
    DockerError,
    HomeAssistantAPIError,
    HostAppArmorError,
)
from ..hardware.data import Device
from ..homeassistant.const import WSEvent
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from ..resolution.const import ContextType, IssueType, UnhealthyReason
from ..resolution.data import Issue
from ..store.addon import AddonStore
from ..utils import check_port
from ..utils.apparmor import adjust_profile
from ..utils.json import read_json_file, write_json_file
from ..utils.sentry import async_capture_exception
from .const import (
    WATCHDOG_MAX_ATTEMPTS,
    WATCHDOG_RETRY_SECONDS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
    AddonBackupMode,
    MappingType,
)
from .model import AddonModel, Data
from .options import AddonOptions
from .utils import remove_data
from .validate import SCHEMA_ADDON_BACKUP

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_WEBUI = re.compile(
    r"^(?:(?P<s_prefix>https?)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:\[PORT:(?P<t_port>\d+)\](?P<s_suffix>.*)$"
)

RE_WATCHDOG = re.compile(
    r"^(?:(?P<s_prefix>https?|tcp)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:(?:\[PORT:)?(?P<t_port>\d+)\]?(?P<s_suffix>.*)$"
)

WATCHDOG_TIMEOUT = aiohttp.ClientTimeout(total=10)
STARTUP_TIMEOUT = 120

_OPTIONS_MERGER: Final = Merger(
    type_strategies=[(dict, ["merge"])],
    fallback_strategies=["override"],
    type_conflict_strategies=["override"],
)

# Backups just need to know if an addon was running or not
# Map other addon states to those two
_MAP_ADDON_STATE = {
    AddonState.STARTUP: AddonState.STARTED,
    AddonState.ERROR: AddonState.STOPPED,
    AddonState.UNKNOWN: AddonState.STOPPED,
}


class Addon(AddonModel):
    """Hold data for add-on inside Supervisor."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        super().__init__(coresys, slug)
        self.instance: DockerAddon = DockerAddon(coresys, self)
        self._state: AddonState = AddonState.UNKNOWN
        self._manual_stop: bool = False
        self._listeners: list[EventListener] = []
        self._startup_event = asyncio.Event()
        self._startup_task: asyncio.Task | None = None
        self._boot_failed_issue = Issue(
            IssueType.BOOT_FAIL, ContextType.ADDON, reference=self.slug
        )
        self._device_access_missing_issue = Issue(
            IssueType.DEVICE_ACCESS_MISSING, ContextType.ADDON, reference=self.slug
        )

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Addon: {self.slug}>"

    @property
    def boot_failed_issue(self) -> Issue:
        """Get issue used if start on boot failed."""
        return self._boot_failed_issue

    @property
    def device_access_missing_issue(self) -> Issue:
        """Get issue used if device access is missing and can't be automatically added."""
        return self._device_access_missing_issue

    @property
    def state(self) -> AddonState:
        """Return state of the add-on."""
        return self._state

    @state.setter
    def state(self, new_state: AddonState) -> None:
        """Set the add-on into new state."""
        if self._state == new_state:
            return
        old_state = self._state
        self._state = new_state

        # Signal listeners about addon state change
        if new_state == AddonState.STARTED or old_state == AddonState.STARTUP:
            self._startup_event.set()

        # Dismiss boot failed issue if present and we started
        if (
            new_state == AddonState.STARTED
            and self.boot_failed_issue in self.sys_resolution.issues
        ):
            self.sys_resolution.dismiss_issue(self.boot_failed_issue)

        # Dismiss device access missing issue if present and we stopped
        if (
            new_state == AddonState.STOPPED
            and self.device_access_missing_issue in self.sys_resolution.issues
        ):
            self.sys_resolution.dismiss_issue(self.device_access_missing_issue)

        self.sys_homeassistant.websocket.supervisor_event_custom(
            WSEvent.ADDON,
            {
                ATTR_SLUG: self.slug,
                ATTR_STATE: new_state,
            },
        )

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Async initialize of object."""
        self._manual_stop = (
            await self.sys_hardware.helper.last_boot() != self.sys_config.last_boot
        )

        if self.is_detached:
            await super().refresh_path_cache()

        self._listeners.append(
            self.sys_bus.register_event(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE, self.container_state_changed
            )
        )
        self._listeners.append(
            self.sys_bus.register_event(
                BusEvent.DOCKER_CONTAINER_STATE_CHANGE, self.watchdog_container
            )
        )

        await self._check_ingress_port()
        default_image = self._image(self.data)
        try:
            await self.instance.attach(version=self.version)

            # Ensure we are using correct image for this system
            await self.instance.check_image(self.version, default_image, self.arch)
        except DockerError:
            _LOGGER.info("No %s addon Docker image %s found", self.slug, self.image)
            with suppress(DockerError):
                await self.instance.install(self.version, default_image, arch=self.arch)

        self.persist[ATTR_IMAGE] = default_image
        await self.save_persist()

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP of add-on instance."""
        return self.instance.ip_address

    @property
    def data(self) -> Data:
        """Return add-on data/config."""
        return self.sys_addons.data.system[self.slug]

    @property
    def data_store(self) -> Data:
        """Return add-on data from store."""
        return self.sys_store.data.addons.get(self.slug, self.data)

    @property
    def addon_store(self) -> AddonStore | None:
        """Return store representation of addon."""
        return self.sys_addons.store.get(self.slug)

    @property
    def persist(self) -> Data:
        """Return add-on data/config."""
        return self.sys_addons.data.user[self.slug]

    @property
    def is_installed(self) -> bool:
        """Return True if an add-on is installed."""
        return True

    @property
    def is_detached(self) -> bool:
        """Return True if add-on is detached."""
        return self.slug not in self.sys_store.data.addons

    @property
    def with_icon(self) -> bool:
        """Return True if an icon exists."""
        if self.is_detached or not self.addon_store:
            return super().with_icon
        return self.addon_store.with_icon

    @property
    def with_logo(self) -> bool:
        """Return True if a logo exists."""
        if self.is_detached or not self.addon_store:
            return super().with_logo
        return self.addon_store.with_logo

    @property
    def with_changelog(self) -> bool:
        """Return True if a changelog exists."""
        if self.is_detached or not self.addon_store:
            return super().with_changelog
        return self.addon_store.with_changelog

    @property
    def with_documentation(self) -> bool:
        """Return True if a documentation exists."""
        if self.is_detached or not self.addon_store:
            return super().with_documentation
        return self.addon_store.with_documentation

    @property
    def available(self) -> bool:
        """Return True if this add-on is available on this platform."""
        return self._available(self.data_store)

    @property
    def version(self) -> AwesomeVersion:
        """Return installed version."""
        return self.persist[ATTR_VERSION]

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        if self.is_detached:
            return False
        return self.version != self.latest_version

    @property
    def dns(self) -> list[str]:
        """Return list of DNS name for that add-on."""
        return [f"{self.hostname}.{DNS_SUFFIX}"]

    @property
    def options(self) -> dict[str, Any]:
        """Return options with local changes."""
        return _OPTIONS_MERGER.merge(
            deepcopy(self.data[ATTR_OPTIONS]), deepcopy(self.persist[ATTR_OPTIONS])
        )

    @options.setter
    def options(self, value: dict[str, Any] | None) -> None:
        """Store user add-on options."""
        self.persist[ATTR_OPTIONS] = {} if value is None else deepcopy(value)

    @property
    def boot(self) -> AddonBoot:
        """Return boot config with prio local settings unless config is forced."""
        if self.boot_config == AddonBootConfig.MANUAL_ONLY:
            return super().boot
        return self.persist.get(ATTR_BOOT, super().boot)

    @boot.setter
    def boot(self, value: AddonBoot) -> None:
        """Store user boot options."""
        self.persist[ATTR_BOOT] = value

        # Dismiss boot failed issue if present and boot at start disabled
        if (
            value == AddonBoot.MANUAL
            and self._boot_failed_issue in self.sys_resolution.issues
        ):
            self.sys_resolution.dismiss_issue(self._boot_failed_issue)

    @property
    def auto_update(self) -> bool:
        """Return if auto update is enable."""
        return self.persist.get(ATTR_AUTO_UPDATE, super().auto_update)

    @auto_update.setter
    def auto_update(self, value: bool) -> None:
        """Set auto update."""
        self.persist[ATTR_AUTO_UPDATE] = value

    @property
    def auto_update_available(self) -> bool:
        """Return if it is safe to auto update addon."""
        if not self.need_update or not self.auto_update:
            return False

        for version in self.breaking_versions:
            try:
                # Must update to latest so if true update crosses a breaking version
                if self.version < version:
                    return False
            except AwesomeVersionCompareException:
                # If version scheme changed, we may get compare exception
                # If latest version >= breaking version then assume update will
                # cross it as the version scheme changes
                # If both versions have compare exception, ignore as its in the past
                with suppress(AwesomeVersionCompareException):
                    if self.latest_version >= version:
                        return False

        return True

    @property
    def watchdog(self) -> bool:
        """Return True if watchdog is enable."""
        return self.persist[ATTR_WATCHDOG]

    @watchdog.setter
    def watchdog(self, value: bool) -> None:
        """Set watchdog enable/disable."""
        if value and self.startup == AddonStartup.ONCE:
            _LOGGER.warning(
                "Ignoring watchdog for %s because startup type is 'once'", self.slug
            )
        else:
            self.persist[ATTR_WATCHDOG] = value

    @property
    def system_managed(self) -> bool:
        """Return True if addon is managed by Home Assistant."""
        return self.persist[ATTR_SYSTEM_MANAGED]

    @system_managed.setter
    def system_managed(self, value: bool) -> None:
        """Set system managed enable/disable."""
        if not value and self.system_managed_config_entry:
            self.system_managed_config_entry = None

        self.persist[ATTR_SYSTEM_MANAGED] = value

    @property
    def system_managed_config_entry(self) -> str | None:
        """Return id of config entry managing this addon (if any)."""
        if not self.system_managed:
            return None
        return self.persist.get(ATTR_SYSTEM_MANAGED_CONFIG_ENTRY)

    @system_managed_config_entry.setter
    def system_managed_config_entry(self, value: str | None) -> None:
        """Set ID of config entry managing this addon."""
        if not self.system_managed:
            _LOGGER.warning(
                "Ignoring system managed config entry for %s because it is not system managed",
                self.slug,
            )
        else:
            self.persist[ATTR_SYSTEM_MANAGED_CONFIG_ENTRY] = value

    @property
    def uuid(self) -> str:
        """Return an API token for this add-on."""
        return self.persist[ATTR_UUID]

    @property
    def supervisor_token(self) -> str | None:
        """Return access token for Supervisor API."""
        return self.persist.get(ATTR_ACCESS_TOKEN)

    @property
    def ingress_token(self) -> str | None:
        """Return access token for Supervisor API."""
        return self.persist.get(ATTR_INGRESS_TOKEN)

    @property
    def ingress_entry(self) -> str | None:
        """Return ingress external URL."""
        if self.with_ingress:
            return f"/api/hassio_ingress/{self.ingress_token}"
        return None

    @property
    def latest_version(self) -> AwesomeVersion:
        """Return version of add-on."""
        return self.data_store[ATTR_VERSION]

    @property
    def latest_version_timestamp(self) -> datetime:
        """Return when latest version was first seen."""
        return utc_from_timestamp(self.data_store[ATTR_VERSION_TIMESTAMP])

    @property
    def protected(self) -> bool:
        """Return if add-on is in protected mode."""
        return self.persist[ATTR_PROTECTED]

    @protected.setter
    def protected(self, value: bool) -> None:
        """Set add-on in protected mode."""
        self.persist[ATTR_PROTECTED] = value

    @property
    def ports(self) -> dict[str, int | None] | None:
        """Return ports of add-on."""
        return self.persist.get(ATTR_NETWORK, super().ports)

    @ports.setter
    def ports(self, value: dict[str, int | None] | None) -> None:
        """Set custom ports of add-on."""
        if value is None:
            self.persist.pop(ATTR_NETWORK, None)
            return

        # Secure map ports to value
        new_ports = {}
        for container_port, host_port in value.items():
            if container_port in self.data.get(ATTR_PORTS, {}):
                new_ports[container_port] = host_port

        self.persist[ATTR_NETWORK] = new_ports

    @property
    def ingress_url(self) -> str | None:
        """Return URL to ingress url."""
        if not self.with_ingress:
            return None

        url = f"/api/hassio_ingress/{self.ingress_token}/"
        if ATTR_INGRESS_ENTRY in self.data:
            return f"{url}{self.data[ATTR_INGRESS_ENTRY]}"
        return url

    @property
    def webui(self) -> str | None:
        """Return URL to webui or None."""
        url = super().webui
        if not url or not (webui := RE_WEBUI.match(url)):
            return None

        # extract arguments
        t_port = webui.group("t_port")
        t_proto = webui.group("t_proto")
        s_prefix = webui.group("s_prefix") or ""
        s_suffix = webui.group("s_suffix") or ""

        # search host port for this docker port
        if self.ports is None:
            port = t_port
        else:
            port = self.ports.get(f"{t_port}/tcp", t_port)

        # lookup the correct protocol from config
        if t_proto:
            proto = "https" if self.options.get(t_proto) else "http"
        else:
            proto = s_prefix

        return f"{proto}://[HOST]:{port}{s_suffix}"

    @property
    def ingress_port(self) -> int | None:
        """Return Ingress port."""
        if not self.with_ingress:
            return None

        port = self.data[ATTR_INGRESS_PORT]
        if port == 0:
            raise RuntimeError(f"No port set for add-on {self.slug}")
        return port

    @property
    def ingress_panel(self) -> bool | None:
        """Return True if the add-on access support ingress."""
        if not self.with_ingress:
            return None

        return self.persist[ATTR_INGRESS_PANEL]

    @ingress_panel.setter
    def ingress_panel(self, value: bool) -> None:
        """Return True if the add-on access support ingress."""
        self.persist[ATTR_INGRESS_PANEL] = value

    @property
    def audio_output(self) -> str | None:
        """Return a pulse profile for output or None."""
        if not self.with_audio:
            return None
        return self.persist.get(ATTR_AUDIO_OUTPUT)

    @audio_output.setter
    def audio_output(self, value: str | None):
        """Set audio output profile settings."""
        self.persist[ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self) -> str | None:
        """Return pulse profile for input or None."""
        if not self.with_audio:
            return None

        return self.persist.get(ATTR_AUDIO_INPUT)

    @audio_input.setter
    def audio_input(self, value: str | None) -> None:
        """Set audio input settings."""
        self.persist[ATTR_AUDIO_INPUT] = value

    @property
    def image(self) -> str | None:
        """Return image name of add-on."""
        return self.persist.get(ATTR_IMAGE)

    @property
    def need_build(self) -> bool:
        """Return True if this  add-on need a local build."""
        return ATTR_IMAGE not in self.data

    @property
    def latest_need_build(self) -> bool:
        """Return True if the latest version of the addon needs a local build."""
        return ATTR_IMAGE not in self.data_store

    @property
    def path_data(self) -> Path:
        """Return add-on data path inside Supervisor."""
        return Path(self.sys_config.path_addons_data, self.slug)

    @property
    def path_extern_data(self) -> PurePath:
        """Return add-on data path external for Docker."""
        return PurePath(self.sys_config.path_extern_addons_data, self.slug)

    @property
    def addon_config_used(self) -> bool:
        """Add-on is using its public config folder."""
        return MappingType.ADDON_CONFIG in self.map_volumes

    @property
    def path_config(self) -> Path:
        """Return add-on config path inside Supervisor."""
        return Path(self.sys_config.path_addon_configs, self.slug)

    @property
    def path_extern_config(self) -> PurePath:
        """Return add-on config path external for Docker."""
        return PurePath(self.sys_config.path_extern_addon_configs, self.slug)

    @property
    def path_options(self) -> Path:
        """Return path to add-on options."""
        return Path(self.path_data, "options.json")

    @property
    def path_pulse(self) -> Path:
        """Return path to asound config."""
        return Path(self.sys_config.path_tmp, f"{self.slug}_pulse")

    @property
    def path_extern_pulse(self) -> Path:
        """Return path to asound config for Docker."""
        return Path(self.sys_config.path_extern_tmp, f"{self.slug}_pulse")

    @property
    def devices(self) -> set[Device]:
        """Extract devices from add-on options."""
        options_schema = self.schema
        with suppress(vol.Invalid):
            options_schema.validate(self.options)

        return options_schema.devices

    @property
    def pwned(self) -> set[str]:
        """Extract pwned data for add-on options."""
        options_schema = self.schema
        with suppress(vol.Invalid):
            options_schema.validate(self.options)

        return options_schema.pwned

    @property
    def loaded(self) -> bool:
        """Is add-on loaded."""
        return bool(self._listeners)

    async def save_persist(self) -> None:
        """Save data of add-on."""
        await self.sys_addons.data.save_data()

    async def watchdog_application(self) -> bool:
        """Return True if application is running."""
        url = self.watchdog_url
        if not url or not (application := RE_WATCHDOG.match(url)):
            return True

        # extract arguments
        t_port = int(application.group("t_port"))
        t_proto = application.group("t_proto")
        s_prefix = application.group("s_prefix") or ""
        s_suffix = application.group("s_suffix") or ""

        # search host port for this docker port
        if self.host_network and self.ports:
            port = self.ports.get(f"{t_port}/tcp")
            if port is None:
                port = t_port
        else:
            port = t_port

        # TCP monitoring
        if s_prefix == "tcp":
            return await check_port(self.ip_address, port)

        # lookup the correct protocol from config
        if t_proto:
            proto = "https" if self.options.get(t_proto) else "http"
        else:
            proto = s_prefix

        # Make HTTP request
        try:
            url = f"{proto}://{self.ip_address}:{port}{s_suffix}"
            async with self.sys_websession.get(
                url, timeout=WATCHDOG_TIMEOUT, ssl=False
            ) as req:
                if req.status < 300:
                    return True
        except (TimeoutError, aiohttp.ClientError):
            pass

        return False

    async def write_options(self) -> None:
        """Return True if add-on options is written to data."""
        # Update secrets for validation
        await self.sys_homeassistant.secrets.reload()

        try:
            options = self.schema.validate(self.options)
            await self.sys_run_in_executor(write_json_file, self.path_options, options)
        except vol.Invalid as ex:
            _LOGGER.error(
                "Add-on %s has invalid options: %s",
                self.slug,
                humanize_error(self.options, ex),
            )
        except ConfigurationFileError:
            _LOGGER.error("Add-on %s can't write options", self.slug)
        else:
            _LOGGER.debug("Add-on %s write options: %s", self.slug, options)
            return

        raise AddonConfigurationError()

    @Job(
        name="addon_unload",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def unload(self) -> None:
        """Unload add-on and remove data."""
        if self._startup_task:
            # If we were waiting on startup, cancel that and let the task finish before proceeding
            self._startup_task.cancel(f"Removing add-on {self.name} from system")
            with suppress(asyncio.CancelledError):
                await self._startup_task

        for listener in self._listeners:
            self.sys_bus.remove_listener(listener)

        def remove_data_dir():
            if self.path_data.is_dir():
                _LOGGER.info("Removing add-on data folder %s", self.path_data)
                remove_data(self.path_data)

        await self.sys_run_in_executor(remove_data_dir)

    async def _check_ingress_port(self):
        """Assign a ingress port if dynamic port selection is used."""
        if not self.with_ingress:
            return

        if self.data[ATTR_INGRESS_PORT] == 0:
            self.data[ATTR_INGRESS_PORT] = await self.sys_ingress.get_dynamic_port(
                self.slug
            )

    @Job(
        name="addon_install",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def install(self) -> None:
        """Install and setup this addon."""
        if not self.addon_store:
            raise AddonsError("Missing from store, cannot install!")

        await self.sys_addons.data.install(self.addon_store)
        await self.load()

        def setup_data():
            if not self.path_data.is_dir():
                _LOGGER.info(
                    "Creating Home Assistant add-on data folder %s", self.path_data
                )
                self.path_data.mkdir()

        await self.sys_run_in_executor(setup_data)

        # Setup/Fix AppArmor profile
        await self.install_apparmor()

        # Install image
        try:
            await self.instance.install(
                self.latest_version, self.addon_store.image, arch=self.arch
            )
        except DockerError as err:
            await self.sys_addons.data.uninstall(self)
            raise AddonsError() from err

        # Add to addon manager
        self.sys_addons.local[self.slug] = self

        # Reload ingress tokens
        if self.with_ingress:
            await self.sys_ingress.reload()

    @Job(
        name="addon_uninstall",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def uninstall(
        self, *, remove_config: bool, remove_image: bool = True
    ) -> None:
        """Uninstall and cleanup this addon."""
        try:
            await self.instance.remove(remove_image=remove_image)
        except DockerError as err:
            raise AddonsError() from err

        self.state = AddonState.UNKNOWN

        await self.unload()

        def cleanup_config_and_audio():
            # Remove config if present and requested
            if self.addon_config_used and remove_config:
                remove_data(self.path_config)

            # Cleanup audio settings
            if self.path_pulse.exists():
                with suppress(OSError):
                    self.path_pulse.unlink()

        await self.sys_run_in_executor(cleanup_config_and_audio)

        # Cleanup AppArmor profile
        with suppress(HostAppArmorError):
            await self.uninstall_apparmor()

        # Cleanup Ingress panel from sidebar
        if self.ingress_panel:
            self.ingress_panel = False
            with suppress(HomeAssistantAPIError):
                await self.sys_ingress.update_hass_panel(self)

        # Cleanup Ingress dynamic port assignment
        need_ingress_token_cleanup = False
        if self.with_ingress:
            need_ingress_token_cleanup = True
            await self.sys_ingress.del_dynamic_port(self.slug)

        # Cleanup discovery data
        for message in self.sys_discovery.list_messages:
            if message.addon != self.slug:
                continue
            await self.sys_discovery.remove(message)

        # Cleanup services data
        for service in self.sys_services.list_services:
            if self.slug not in service.active:
                continue
            await service.del_service_data(self)

        # Remove from addon manager
        self.sys_addons.local.pop(self.slug)
        await self.sys_addons.data.uninstall(self)

        # Cleanup Ingress tokens
        if need_ingress_token_cleanup:
            await self.sys_ingress.reload()

    @Job(
        name="addon_update",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def update(self) -> asyncio.Task | None:
        """Update this addon to latest version.

        Returns a Task that completes when addon has state 'started' (see start)
        if it was running. Else nothing is returned.
        """
        if not self.addon_store:
            raise AddonsError("Missing from store, cannot update!")

        old_image = self.image
        # Cache data to prevent races with other updates to global
        store = self.addon_store.clone()

        try:
            await self.instance.update(store.version, store.image, arch=self.arch)
        except DockerError as err:
            raise AddonsError() from err

        # Stop the addon if running
        if (last_state := self.state) in {AddonState.STARTED, AddonState.STARTUP}:
            await self.stop()

        try:
            _LOGGER.info("Add-on '%s' successfully updated", self.slug)
            await self.sys_addons.data.update(store)
            await self._check_ingress_port()

            # Cleanup
            with suppress(DockerError):
                await self.instance.cleanup(
                    old_image=old_image, image=store.image, version=store.version
                )

            # Setup/Fix AppArmor profile
            await self.install_apparmor()

        finally:
            # restore state. Return Task for caller if no exception
            out = (
                await self.start()
                if last_state in {AddonState.STARTED, AddonState.STARTUP}
                else None
            )
        return out

    @Job(
        name="addon_rebuild",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def rebuild(self) -> asyncio.Task | None:
        """Rebuild this addons container and image.

        Returns a Task that completes when addon has state 'started' (see start)
        if it was running. Else nothing is returned.
        """
        last_state: AddonState = self.state
        try:
            # remove docker container but not addon config
            try:
                await self.instance.remove()
                await self.instance.install(self.version)
            except DockerError as err:
                raise AddonsError() from err

            if self.addon_store:
                await self.sys_addons.data.update(self.addon_store)

            await self._check_ingress_port()
            _LOGGER.info("Add-on '%s' successfully rebuilt", self.slug)

        finally:
            # restore state
            out = (
                await self.start()
                if last_state in [AddonState.STARTED, AddonState.STARTUP]
                else None
            )
        return out

    async def write_pulse(self) -> None:
        """Write asound config to file and return True on success."""
        pulse_config = self.sys_plugins.audio.pulse_client(
            input_profile=self.audio_input, output_profile=self.audio_output
        )

        def write_pulse_config():
            # Cleanup wrong maps
            if self.path_pulse.is_dir():
                shutil.rmtree(self.path_pulse, ignore_errors=True)
            self.path_pulse.write_text(pulse_config, encoding="utf-8")

        try:
            await self.sys_run_in_executor(write_pulse_config)
        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            _LOGGER.error(
                "Add-on %s can't write pulse/client.config: %s", self.slug, err
            )
        else:
            _LOGGER.debug(
                "Add-on %s write pulse/client.config: %s", self.slug, self.path_pulse
            )

    async def install_apparmor(self) -> None:
        """Install or Update AppArmor profile for Add-on."""
        exists_local = self.sys_host.apparmor.exists(self.slug)
        exists_addon = await self.sys_run_in_executor(self.path_apparmor.exists)

        # Nothing to do
        if not exists_local and not exists_addon:
            return

        # Need removed
        if exists_local and not exists_addon:
            await self.sys_host.apparmor.remove_profile(self.slug)
            return

        # Need install/update
        tmp_folder: TemporaryDirectory | None = None

        def install_update_profile() -> Path:
            nonlocal tmp_folder
            tmp_folder = TemporaryDirectory(dir=self.sys_config.path_tmp)
            profile_file = Path(tmp_folder.name, "apparmor.txt")
            adjust_profile(self.slug, self.path_apparmor, profile_file)
            return profile_file

        try:
            profile_file = await self.sys_run_in_executor(install_update_profile)
            await self.sys_host.apparmor.load_profile(self.slug, profile_file)
        finally:
            if tmp_folder:
                await self.sys_run_in_executor(tmp_folder.cleanup)

    async def uninstall_apparmor(self) -> None:
        """Remove AppArmor profile for Add-on."""
        if not self.sys_host.apparmor.exists(self.slug):
            return
        await self.sys_host.apparmor.remove_profile(self.slug)

    def test_update_schema(self) -> bool:
        """Check if the existing configuration is valid after update."""
        # load next schema
        new_raw_schema = self.data_store[ATTR_SCHEMA]
        default_options = self.data_store[ATTR_OPTIONS]

        # if disabled
        if isinstance(new_raw_schema, bool):
            return True

        # merge options
        options = _OPTIONS_MERGER.merge(
            deepcopy(default_options), deepcopy(self.persist[ATTR_OPTIONS])
        )

        # create voluptuous
        new_schema = vol.Schema(
            vol.All(
                dict, AddonOptions(self.coresys, new_raw_schema, self.name, self.slug)
            )
        )

        # validate
        try:
            new_schema(options)
        except vol.Invalid:
            _LOGGER.warning("Add-on %s new schema is not compatible", self.slug)
            return False
        return True

    async def _wait_for_startup(self) -> None:
        """Wait for startup event to be set with timeout."""
        try:
            self._startup_task = self.sys_create_task(self._startup_event.wait())
            await asyncio.wait_for(self._startup_task, STARTUP_TIMEOUT)
        except TimeoutError:
            _LOGGER.warning(
                "Timeout while waiting for addon %s to start, took more than %s seconds",
                self.name,
                STARTUP_TIMEOUT,
            )
        except asyncio.CancelledError as err:
            _LOGGER.info("Wait for addon startup task cancelled due to: %s", err)
        finally:
            self._startup_task = None

    @Job(
        name="addon_start",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def start(self) -> asyncio.Task:
        """Set options and start add-on.

        Returns a Task that completes when addon has state 'started'.
        For addons with a healthcheck, that is when they become healthy or unhealthy.
        Addons without a healthcheck have state 'started' immediately.
        """
        if await self.instance.is_running():
            _LOGGER.warning("%s is already running!", self.slug)
            return self.sys_create_task(self._wait_for_startup())

        # Access Token
        self.persist[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        await self.save_persist()

        # Options
        await self.write_options()

        # Sound
        if self.with_audio:
            await self.write_pulse()

        def _check_addon_config_dir():
            if self.path_config.is_dir():
                return

            _LOGGER.info(
                "Creating Home Assistant add-on config folder %s", self.path_config
            )
            self.path_config.mkdir()

        if self.addon_config_used:
            await self.sys_run_in_executor(_check_addon_config_dir)

        # Start Add-on
        self._startup_event.clear()
        try:
            await self.instance.run()
        except DockerError as err:
            self.state = AddonState.ERROR
            raise AddonsError() from err

        return self.sys_create_task(self._wait_for_startup())

    @Job(
        name="addon_stop",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def stop(self) -> None:
        """Stop add-on."""
        self._manual_stop = True
        try:
            await self.instance.stop()
        except DockerError as err:
            self.state = AddonState.ERROR
            raise AddonsError() from err

    @Job(
        name="addon_restart",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def restart(self) -> asyncio.Task:
        """Restart add-on.

        Returns a Task that completes when addon has state 'started' (see start).
        """
        with suppress(AddonsError):
            await self.stop()
        return await self.start()

    def logs(self) -> Awaitable[bytes]:
        """Return add-ons log output.

        Return a coroutine.
        """
        return self.instance.logs()

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    async def stats(self) -> DockerStats:
        """Return stats of container."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise AddonsError() from err

    @Job(
        name="addon_write_stdin",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def write_stdin(self, data) -> None:
        """Write data to add-on stdin."""
        if not self.with_stdin:
            raise AddonsNotSupportedError(
                f"Add-on {self.slug} does not support writing to stdin!", _LOGGER.error
            )

        try:
            return await self.instance.write_stdin(data)
        except DockerError as err:
            raise AddonsError() from err

    async def _backup_command(self, command: str) -> None:
        try:
            command_return = await self.instance.run_inside(command)
            if command_return.exit_code != 0:
                _LOGGER.debug(
                    "Pre-/Post backup command failed with: %s", command_return.output
                )
                raise AddonsError(
                    f"Pre-/Post backup command returned error code: {command_return.exit_code}",
                    _LOGGER.error,
                )
        except DockerError as err:
            raise AddonsError(
                f"Failed running pre-/post backup command {command}: {str(err)}",
                _LOGGER.error,
            ) from err

    @Job(
        name="addon_begin_backup",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def begin_backup(self) -> bool:
        """Execute pre commands or stop addon if necessary.

        Returns value of `is_running`. Caller should not call `end_backup` if return is false.
        """
        if not await self.is_running():
            return False

        if self.backup_mode == AddonBackupMode.COLD:
            _LOGGER.info("Shutdown add-on %s for cold backup", self.slug)
            await self.stop()

        elif self.backup_pre is not None:
            await self._backup_command(self.backup_pre)

        return True

    @Job(
        name="addon_end_backup",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def end_backup(self) -> asyncio.Task | None:
        """Execute post commands or restart addon if necessary.

        Returns a Task that completes when addon has state 'started' (see start)
        for cold backup. Else nothing is returned.
        """
        if self.backup_mode is AddonBackupMode.COLD:
            _LOGGER.info("Starting add-on %s again", self.slug)
            return await self.start()

        if self.backup_post is not None:
            await self._backup_command(self.backup_post)
        return None

    def _is_excluded_by_filter(
        self, origin_path: Path, arcname: str, item_arcpath: PurePath
    ) -> bool:
        """Filter out files from backup based on filters provided by addon developer.

        This tests the dev provided filters against the full path of the file as
        Supervisor sees them using match. This is done for legacy reasons, testing
        against the relative path makes more sense and may be changed in the future.
        """
        full_path = origin_path / item_arcpath.relative_to(arcname)

        for exclude in self.backup_exclude:
            if not full_path.match(exclude):
                continue
            _LOGGER.debug("Ignoring %s because of %s", full_path, exclude)
            return True

        return False

    @Job(
        name="addon_backup",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def backup(self, tar_file: tarfile.TarFile) -> asyncio.Task | None:
        """Backup state of an add-on.

        Returns a Task that completes when addon has state 'started' (see start)
        for cold backup. Else nothing is returned.
        """

        def _addon_backup(
            store_image: bool,
            metadata: dict[str, Any],
            apparmor_profile: str | None,
            addon_config_used: bool,
        ):
            """Start the backup process."""
            with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
                temp_path = Path(temp)

                # store local image
                if store_image:
                    try:
                        self.instance.export_image(temp_path.joinpath("image.tar"))
                    except DockerError as err:
                        raise AddonsError() from err

                # Store local configs/state
                try:
                    write_json_file(temp_path.joinpath("addon.json"), metadata)
                except ConfigurationFileError as err:
                    raise AddonsError(
                        f"Can't save meta for {self.slug}", _LOGGER.error
                    ) from err

                # Store AppArmor Profile
                if apparmor_profile:
                    profile_backup_file = temp_path.joinpath("apparmor.txt")
                    try:
                        self.sys_host.apparmor.backup_profile(
                            apparmor_profile, profile_backup_file
                        )
                    except HostAppArmorError as err:
                        raise AddonsError(
                            "Can't backup AppArmor profile", _LOGGER.error
                        ) from err

                # Write tarfile
                with tar_file as backup:
                    # Backup metadata
                    backup.add(temp, arcname=".")

                    # Backup data
                    atomic_contents_add(
                        backup,
                        self.path_data,
                        file_filter=partial(
                            self._is_excluded_by_filter, self.path_data, "data"
                        ),
                        arcname="data",
                    )

                    # Backup config (if used and existing, restore handles this gracefully)
                    if addon_config_used and self.path_config.is_dir():
                        atomic_contents_add(
                            backup,
                            self.path_config,
                            file_filter=partial(
                                self._is_excluded_by_filter, self.path_config, "config"
                            ),
                            arcname="config",
                        )

        wait_for_start: asyncio.Task | None = None

        data = {
            ATTR_USER: self.persist,
            ATTR_SYSTEM: self.data,
            ATTR_VERSION: self.version,
            ATTR_STATE: _MAP_ADDON_STATE.get(self.state, self.state),
        }
        apparmor_profile = (
            self.slug if self.sys_host.apparmor.exists(self.slug) else None
        )

        was_running = await self.begin_backup()
        try:
            _LOGGER.info("Building backup for add-on %s", self.slug)
            await self.sys_run_in_executor(
                partial(
                    _addon_backup,
                    store_image=self.need_build,
                    metadata=data,
                    apparmor_profile=apparmor_profile,
                    addon_config_used=self.addon_config_used,
                )
            )
            _LOGGER.info("Finish backup for addon %s", self.slug)
        except (tarfile.TarError, OSError, AddFileError) as err:
            raise AddonsError(f"Can't write tarfile: {err}", _LOGGER.error) from err
        finally:
            if was_running:
                wait_for_start = await self.end_backup()

        return wait_for_start

    @Job(
        name="addon_restore",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=AddonsJobError,
    )
    async def restore(self, tar_file: tarfile.TarFile) -> asyncio.Task | None:
        """Restore state of an add-on.

        Returns a Task that completes when addon has state 'started' (see start)
        if addon is started after restore. Else nothing is returned.
        """
        wait_for_start: asyncio.Task | None = None

        # Extract backup
        def _extract_tarfile() -> tuple[TemporaryDirectory, dict[str, Any]]:
            """Extract tar backup."""
            tmp = TemporaryDirectory(dir=self.sys_config.path_tmp)
            try:
                with tar_file as backup:
                    backup.extractall(
                        path=tmp.name,
                        members=secure_path(backup),
                        filter="fully_trusted",
                    )

                data = read_json_file(Path(tmp.name, "addon.json"))
            except:
                tmp.cleanup()
                raise

            return tmp, data

        try:
            tmp, data = await self.sys_run_in_executor(_extract_tarfile)
        except tarfile.TarError as err:
            raise AddonsError(
                f"Can't read tarfile {tar_file}: {err}", _LOGGER.error
            ) from err
        except ConfigurationFileError as err:
            raise AddonsError() from err

        try:
            # Validate
            try:
                data = SCHEMA_ADDON_BACKUP(data)
            except vol.Invalid as err:
                raise AddonsError(
                    f"Can't validate {self.slug}, backup data: {humanize_error(data, err)}",
                    _LOGGER.error,
                ) from err

            # If available
            if not self._available(data[ATTR_SYSTEM]):
                raise AddonsNotSupportedError(
                    f"Add-on {self.slug} is not available for this platform",
                    _LOGGER.error,
                )

            # Restore local add-on information
            _LOGGER.info("Restore config for addon %s", self.slug)
            restore_image = self._image(data[ATTR_SYSTEM])
            await self.sys_addons.data.restore(
                self.slug, data[ATTR_USER], data[ATTR_SYSTEM], restore_image
            )

            # Stop it first if its running
            if await self.instance.is_running():
                await self.stop()

            try:
                # Check version / restore image
                version = data[ATTR_VERSION]
                if not await self.instance.exists():
                    _LOGGER.info("Restore/Install of image for addon %s", self.slug)

                    image_file = Path(tmp.name, "image.tar")
                    if image_file.is_file():
                        with suppress(DockerError):
                            await self.instance.import_image(image_file)
                    else:
                        with suppress(DockerError):
                            await self.instance.install(
                                version, restore_image, self.arch
                            )
                            await self.instance.cleanup()
                elif self.instance.version != version or self.legacy:
                    _LOGGER.info("Restore/Update of image for addon %s", self.slug)
                    with suppress(DockerError):
                        await self.instance.update(version, restore_image, self.arch)
                await self._check_ingress_port()

                # Restore data and config
                def _restore_data():
                    """Restore data and config."""
                    _LOGGER.info("Restoring data and config for addon %s", self.slug)
                    if self.path_data.is_dir():
                        remove_data(self.path_data)
                    if self.path_config.is_dir():
                        remove_data(self.path_config)

                    temp_data = Path(tmp.name, "data")
                    if temp_data.is_dir():
                        shutil.copytree(temp_data, self.path_data, symlinks=True)
                    else:
                        self.path_data.mkdir()

                    temp_config = Path(tmp.name, "config")
                    if temp_config.is_dir():
                        shutil.copytree(temp_config, self.path_config, symlinks=True)
                    elif self.addon_config_used:
                        self.path_config.mkdir()

                try:
                    await self.sys_run_in_executor(_restore_data)
                except shutil.Error as err:
                    raise AddonsError(
                        f"Can't restore origin data: {err}", _LOGGER.error
                    ) from err

                # Restore AppArmor
                profile_file = Path(tmp.name, "apparmor.txt")
                if await self.sys_run_in_executor(profile_file.exists):
                    try:
                        await self.sys_host.apparmor.load_profile(
                            self.slug, profile_file
                        )
                    except HostAppArmorError as err:
                        _LOGGER.error(
                            "Can't restore AppArmor profile for add-on %s",
                            self.slug,
                        )
                        raise AddonsError() from err

            finally:
                # Is add-on loaded
                if not self.loaded:
                    await self.load()

                # Run add-on
                if data[ATTR_STATE] == AddonState.STARTED:
                    wait_for_start = await self.start()
        finally:
            await self.sys_run_in_executor(tmp.cleanup)
        _LOGGER.info("Finished restore for add-on %s", self.slug)
        return wait_for_start

    def check_trust(self) -> Awaitable[None]:
        """Calculate Addon docker content trust.

        Return Coroutine.
        """
        return self.instance.check_trust()

    @Job(
        name="addon_restart_after_problem",
        limit=JobExecutionLimit.GROUP_THROTTLE_RATE_LIMIT,
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=AddonsJobError,
    )
    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed addon."""
        attempts = 0
        while await self.instance.current_state() == state:
            if not self.in_progress:
                _LOGGER.warning(
                    "Watchdog found addon %s is %s, restarting...",
                    self.name,
                    state,
                )
                try:
                    if state == ContainerState.FAILED:
                        # Ensure failed container is removed before attempting reanimation
                        if attempts == 0:
                            with suppress(DockerError):
                                await self.instance.stop(remove_container=True)

                        await (await self.start())
                    else:
                        await (await self.restart())
                except AddonsError as err:
                    attempts = attempts + 1
                    _LOGGER.error("Watchdog restart of addon %s failed!", self.name)
                    await async_capture_exception(err)
                else:
                    break

            if attempts >= WATCHDOG_MAX_ATTEMPTS:
                _LOGGER.critical(
                    "Watchdog cannot restart addon %s, failed all %s attempts",
                    self.name,
                    attempts,
                )
                break

            await asyncio.sleep(WATCHDOG_RETRY_SECONDS)

    async def container_state_changed(self, event: DockerContainerStateEvent) -> None:
        """Set addon state from container state."""
        if event.name != self.instance.name:
            return

        if event.state == ContainerState.RUNNING:
            self._manual_stop = False
            self.state = (
                AddonState.STARTUP if self.instance.healthcheck else AddonState.STARTED
            )
        elif event.state in [
            ContainerState.HEALTHY,
            ContainerState.UNHEALTHY,
        ]:
            self.state = AddonState.STARTED
        elif event.state == ContainerState.STOPPED:
            self.state = AddonState.STOPPED
        elif event.state == ContainerState.FAILED:
            self.state = AddonState.ERROR

    async def watchdog_container(self, event: DockerContainerStateEvent) -> None:
        """Process state changes in addon container and restart if necessary."""
        if event.name != self.instance.name:
            return

        # Skip watchdog if not enabled or manual stopped
        if not self.watchdog or self._manual_stop:
            return

        if event.state in [
            ContainerState.FAILED,
            ContainerState.STOPPED,
            ContainerState.UNHEALTHY,
        ]:
            await self._restart_after_problem(event.state)

    def refresh_path_cache(self) -> Awaitable[None]:
        """Refresh cache of existing paths."""
        if self.is_detached or not self.addon_store:
            return super().refresh_path_cache()
        return self.addon_store.refresh_path_cache()
