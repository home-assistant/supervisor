"""Init file for Supervisor add-ons."""
import asyncio
from collections.abc import Awaitable
from contextlib import suppress
from copy import deepcopy
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
from deepmerge import Merger
from securetar import atomic_contents_add, secure_path
import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..bus import EventListener
from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_AUTO_UPDATE,
    ATTR_BOOT,
    ATTR_DATA,
    ATTR_EVENT,
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
    ATTR_TYPE,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WATCHDOG,
    DNS_SUFFIX,
    AddonBoot,
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
    HostAppArmorError,
)
from ..hardware.data import Device
from ..homeassistant.const import WSEvent, WSType
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from ..utils import check_port
from ..utils.apparmor import adjust_profile
from ..utils.json import read_json_file, write_json_file
from ..utils.sentry import capture_exception
from .const import (
    WATCHDOG_MAX_ATTEMPTS,
    WATCHDOG_RETRY_SECONDS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
    AddonBackupMode,
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
        self._manual_stop: bool = (
            self.sys_hardware.helper.last_boot != self.sys_config.last_boot
        )
        self._listeners: list[EventListener] = []
        self._startup_event = asyncio.Event()
        self._startup_task: asyncio.Task | None = None

        @Job(
            name=f"addon_{slug}_restart_after_problem",
            limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
            throttle_period=WATCHDOG_THROTTLE_PERIOD,
            throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
            on_condition=AddonsJobError,
        )
        async def restart_after_problem(addon: Addon, state: ContainerState):
            """Restart unhealthy or failed addon."""
            attempts = 0
            while await addon.instance.current_state() == state:
                if not addon.in_progress:
                    _LOGGER.warning(
                        "Watchdog found addon %s is %s, restarting...",
                        addon.name,
                        state.value,
                    )
                    try:
                        if state == ContainerState.FAILED:
                            # Ensure failed container is removed before attempting reanimation
                            if attempts == 0:
                                with suppress(DockerError):
                                    await addon.instance.stop(remove_container=True)

                            await (await addon.start())
                        else:
                            await (await addon.restart())
                    except AddonsError as err:
                        attempts = attempts + 1
                        _LOGGER.error(
                            "Watchdog restart of addon %s failed!", addon.name
                        )
                        capture_exception(err)
                    else:
                        break

                if attempts >= WATCHDOG_MAX_ATTEMPTS:
                    _LOGGER.critical(
                        "Watchdog cannot restart addon %s, failed all %s attempts",
                        addon.name,
                        attempts,
                    )
                    break

                await asyncio.sleep(WATCHDOG_RETRY_SECONDS)

        self._restart_after_problem = restart_after_problem

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Addon: {self.slug}>"

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

        self.sys_homeassistant.websocket.send_message(
            {
                ATTR_TYPE: WSType.SUPERVISOR_EVENT,
                ATTR_DATA: {
                    ATTR_EVENT: WSEvent.ADDON,
                    ATTR_SLUG: self.slug,
                    ATTR_STATE: new_state,
                },
            }
        )

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Async initialize of object."""
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

        with suppress(DockerError):
            await self.instance.attach(version=self.version)

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
    def available(self) -> bool:
        """Return True if this add-on is available on this platform."""
        return self._available(self.data_store)

    @property
    def version(self) -> str | None:
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
        """Return boot config with prio local settings."""
        return self.persist.get(ATTR_BOOT, super().boot)

    @boot.setter
    def boot(self, value: AddonBoot) -> None:
        """Store user boot options."""
        self.persist[ATTR_BOOT] = value

    @property
    def auto_update(self) -> bool:
        """Return if auto update is enable."""
        return self.persist.get(ATTR_AUTO_UPDATE, super().auto_update)

    @auto_update.setter
    def auto_update(self, value: bool) -> None:
        """Set auto update."""
        self.persist[ATTR_AUTO_UPDATE] = value

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
    def latest_version(self) -> str:
        """Return version of add-on."""
        return self.data_store[ATTR_VERSION]

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
        if not url:
            return None
        webui = RE_WEBUI.match(url)

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
            return self.sys_ingress.get_dynamic_port(self.slug)
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

    def save_persist(self) -> None:
        """Save data of add-on."""
        self.sys_addons.data.save_data()

    async def watchdog_application(self) -> bool:
        """Return True if application is running."""
        url = super().watchdog
        if not url:
            return True
        application = RE_WATCHDOG.match(url)

        # extract arguments
        t_port = int(application.group("t_port"))
        t_proto = application.group("t_proto")
        s_prefix = application.group("s_prefix") or ""
        s_suffix = application.group("s_suffix") or ""

        # search host port for this docker port
        if self.host_network:
            port = self.ports.get(f"{t_port}/tcp", t_port)
        else:
            port = t_port

        # TCP monitoring
        if s_prefix == "tcp":
            return await self.sys_run_in_executor(check_port, self.ip_address, port)

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
        except (asyncio.TimeoutError, aiohttp.ClientError):
            pass

        return False

    async def write_options(self) -> None:
        """Return True if add-on options is written to data."""
        # Update secrets for validation
        await self.sys_homeassistant.secrets.reload()

        try:
            options = self.schema.validate(self.options)
            write_json_file(self.path_options, options)
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

    async def unload(self) -> None:
        """Unload add-on and remove data."""
        if self._startup_task:
            # If we were waiting on startup, cancel that and let the task finish before proceeding
            self._startup_task.cancel(f"Removing add-on {self.name} from system")
            with suppress(asyncio.CancelledError):
                await self._startup_task

        for listener in self._listeners:
            self.sys_bus.remove_listener(listener)

        if not self.path_data.is_dir():
            return

        _LOGGER.info("Removing add-on data folder %s", self.path_data)
        await remove_data(self.path_data)

    def write_pulse(self) -> None:
        """Write asound config to file and return True on success."""
        pulse_config = self.sys_plugins.audio.pulse_client(
            input_profile=self.audio_input, output_profile=self.audio_output
        )

        # Cleanup wrong maps
        if self.path_pulse.is_dir():
            shutil.rmtree(self.path_pulse, ignore_errors=True)

        # Write pulse config
        try:
            self.path_pulse.write_text(pulse_config, encoding="utf-8")
        except OSError as err:
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
        exists_addon = self.path_apparmor.exists()

        # Nothing to do
        if not exists_local and not exists_addon:
            return

        # Need removed
        if exists_local and not exists_addon:
            await self.sys_host.apparmor.remove_profile(self.slug)
            return

        # Need install/update
        with TemporaryDirectory(dir=self.sys_config.path_tmp) as tmp_folder:
            profile_file = Path(tmp_folder, "apparmor.txt")

            adjust_profile(self.slug, self.path_apparmor, profile_file)
            await self.sys_host.apparmor.load_profile(self.slug, profile_file)

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
        except asyncio.TimeoutError:
            _LOGGER.warning(
                "Timeout while waiting for addon %s to start, took more then %s seconds",
                self.name,
                STARTUP_TIMEOUT,
            )
        except asyncio.CancelledError as err:
            _LOGGER.info("Wait for addon startup task cancelled due to: %s", err)
        finally:
            self._startup_task = None

    async def start(self) -> Awaitable[None]:
        """Set options and start add-on.

        Returns a coroutine that completes when addon has state 'started'.
        For addons with a healthcheck, that is when they become healthy or unhealthy.
        Addons without a healthcheck have state 'started' immediately.
        """
        if await self.instance.is_running():
            _LOGGER.warning("%s is already running!", self.slug)
            return self._wait_for_startup()

        # Access Token
        self.persist[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        self.save_persist()

        # Options
        await self.write_options()

        # Sound
        if self.with_audio:
            self.write_pulse()

        # Start Add-on
        self._startup_event.clear()
        try:
            await self.instance.run()
        except DockerError as err:
            self.state = AddonState.ERROR
            raise AddonsError() from err

        return self._wait_for_startup()

    async def stop(self) -> None:
        """Stop add-on."""
        self._manual_stop = True
        try:
            await self.instance.stop()
        except DockerError as err:
            self.state = AddonState.ERROR
            raise AddonsError() from err

    async def restart(self) -> Awaitable[None]:
        """Restart add-on.

        Returns a coroutine that completes when addon has state 'started' (see start).
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

    async def backup(self, tar_file: tarfile.TarFile) -> Awaitable[None] | None:
        """Backup state of an add-on.

        Returns a coroutine that completes when addon has state 'started' (see start)
        for cold backup. Else nothing is returned.
        """
        wait_for_start: Awaitable[None] | None = None
        is_running = await self.is_running()

        with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
            temp_path = Path(temp)

            # store local image
            if self.need_build:
                try:
                    await self.instance.export_image(temp_path.joinpath("image.tar"))
                except DockerError as err:
                    raise AddonsError() from err

            data = {
                ATTR_USER: self.persist,
                ATTR_SYSTEM: self.data,
                ATTR_VERSION: self.version,
                ATTR_STATE: _MAP_ADDON_STATE.get(self.state, self.state),
            }

            # Store local configs/state
            try:
                write_json_file(temp_path.joinpath("addon.json"), data)
            except ConfigurationFileError as err:
                raise AddonsError(
                    f"Can't save meta for {self.slug}", _LOGGER.error
                ) from err

            # Store AppArmor Profile
            if self.sys_host.apparmor.exists(self.slug):
                profile = temp_path.joinpath("apparmor.txt")
                try:
                    await self.sys_host.apparmor.backup_profile(self.slug, profile)
                except HostAppArmorError as err:
                    raise AddonsError(
                        "Can't backup AppArmor profile", _LOGGER.error
                    ) from err

            # write into tarfile
            def _write_tarfile():
                """Write tar inside loop."""
                with tar_file as backup:
                    # Backup metadata
                    backup.add(temp, arcname=".")

                    # Backup data
                    atomic_contents_add(
                        backup,
                        self.path_data,
                        excludes=self.backup_exclude,
                        arcname="data",
                    )

            if (
                is_running
                and self.backup_mode == AddonBackupMode.HOT
                and self.backup_pre is not None
            ):
                await self._backup_command(self.backup_pre)
            elif is_running and self.backup_mode == AddonBackupMode.COLD:
                _LOGGER.info("Shutdown add-on %s for cold backup", self.slug)
                try:
                    await self.instance.stop()
                except DockerError as err:
                    raise AddonsError() from err

            try:
                _LOGGER.info("Building backup for add-on %s", self.slug)
                await self.sys_run_in_executor(_write_tarfile)
            except (tarfile.TarError, OSError) as err:
                raise AddonsError(
                    f"Can't write tarfile {tar_file}: {err}", _LOGGER.error
                ) from err
            finally:
                if (
                    is_running
                    and self.backup_mode == AddonBackupMode.HOT
                    and self.backup_post is not None
                ):
                    await self._backup_command(self.backup_post)
                elif is_running and self.backup_mode is AddonBackupMode.COLD:
                    _LOGGER.info("Starting add-on %s again", self.slug)
                    wait_for_start = await self.start()

        _LOGGER.info("Finish backup for addon %s", self.slug)
        return wait_for_start

    async def restore(self, tar_file: tarfile.TarFile) -> Awaitable[None] | None:
        """Restore state of an add-on.

        Returns a coroutine that completes when addon has state 'started' (see start)
        if addon is started after restore. Else nothing is returned.
        """
        wait_for_start: Awaitable[None] | None = None
        with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
            # extract backup
            def _extract_tarfile():
                """Extract tar backup."""
                with tar_file as backup:
                    backup.extractall(path=Path(temp), members=secure_path(backup))

            try:
                await self.sys_run_in_executor(_extract_tarfile)
            except tarfile.TarError as err:
                raise AddonsError(
                    f"Can't read tarfile {tar_file}: {err}", _LOGGER.error
                ) from err

            # Read backup data
            try:
                data = read_json_file(Path(temp, "addon.json"))
            except ConfigurationFileError as err:
                raise AddonsError() from err

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
            self.sys_addons.data.restore(
                self.slug, data[ATTR_USER], data[ATTR_SYSTEM], restore_image
            )

            # Check version / restore image
            version = data[ATTR_VERSION]
            if not await self.instance.exists():
                _LOGGER.info("Restore/Install of image for addon %s", self.slug)

                image_file = Path(temp, "image.tar")
                if image_file.is_file():
                    with suppress(DockerError):
                        await self.instance.import_image(image_file)
                else:
                    with suppress(DockerError):
                        await self.instance.install(version, restore_image)
                        await self.instance.cleanup()
            elif self.instance.version != version or self.legacy:
                _LOGGER.info("Restore/Update of image for addon %s", self.slug)
                with suppress(DockerError):
                    await self.instance.update(version, restore_image)
            else:
                with suppress(DockerError):
                    await self.instance.stop()

            # Restore data
            def _restore_data():
                """Restore data."""
                temp_data = Path(temp, "data")
                if temp_data.is_dir():
                    shutil.copytree(temp_data, self.path_data, symlinks=True)
                else:
                    self.path_data.mkdir()

            _LOGGER.info("Restoring data for addon %s", self.slug)
            if self.path_data.is_dir():
                await remove_data(self.path_data)
            try:
                await self.sys_run_in_executor(_restore_data)
            except shutil.Error as err:
                raise AddonsError(
                    f"Can't restore origin data: {err}", _LOGGER.error
                ) from err

            # Restore AppArmor
            profile_file = Path(temp, "apparmor.txt")
            if profile_file.exists():
                try:
                    await self.sys_host.apparmor.load_profile(self.slug, profile_file)
                except HostAppArmorError as err:
                    _LOGGER.error(
                        "Can't restore AppArmor profile for add-on %s", self.slug
                    )
                    raise AddonsError() from err

            # Is add-on loaded
            if not self.loaded:
                await self.load()

            # Run add-on
            if data[ATTR_STATE] == AddonState.STARTED:
                wait_for_start = await self.start()

        _LOGGER.info("Finished restore for add-on %s", self.slug)
        return wait_for_start

    def check_trust(self) -> Awaitable[None]:
        """Calculate Addon docker content trust.

        Return Coroutine.
        """
        return self.instance.check_trust()

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
            await self._restart_after_problem(self, event.state)
