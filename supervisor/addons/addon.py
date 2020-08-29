"""Init file for Supervisor add-ons."""
import asyncio
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
from typing import Any, Awaitable, Dict, List, Optional

import aiohttp
import voluptuous as vol
from voluptuous.humanize import humanize_error

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
    ATTR_STATE,
    ATTR_SYSTEM,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WATCHDOG,
    DNS_SUFFIX,
    AddonState,
)
from ..coresys import CoreSys
from ..docker.addon import DockerAddon
from ..docker.stats import DockerStats
from ..exceptions import (
    AddonConfigurationError,
    AddonsError,
    AddonsNotSupportedError,
    DockerAPIError,
    HostAppArmorError,
    JsonFileError,
)
from ..utils import check_port
from ..utils.apparmor import adjust_profile
from ..utils.json import read_json_file, write_json_file
from ..utils.tar import atomic_contents_add, secure_path
from .model import AddonModel, Data
from .utils import remove_data
from .validate import SCHEMA_ADDON_SNAPSHOT, validate_options

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_WEBUI = re.compile(
    r"^(?:(?P<s_prefix>https?)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:\[PORT:(?P<t_port>\d+)\](?P<s_suffix>.*)$"
)

RE_WATCHDOG = re.compile(
    r"^(?:(?P<s_prefix>https?|tcp)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:\[PORT:(?P<t_port>\d+)\](?P<s_suffix>.*)$"
)

RE_OLD_AUDIO = re.compile(r"\d+,\d+")

WATCHDOG_TIMEOUT = aiohttp.ClientTimeout(total=10)


class Addon(AddonModel):
    """Hold data for add-on inside Supervisor."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        super().__init__(coresys, slug)
        self.instance: DockerAddon = DockerAddon(coresys, self)
        self.state: AddonState = AddonState.UNKNOWN

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    async def load(self) -> None:
        """Async initialize of object."""
        with suppress(DockerAPIError):
            await self.instance.attach(tag=self.version)

            # Evaluate state
            if await self.instance.is_running():
                self.state = AddonState.STARTED
            else:
                self.state = AddonState.STOPPED

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
    def version(self) -> Optional[str]:
        """Return installed version."""
        return self.persist[ATTR_VERSION]

    @property
    def dns(self) -> List[str]:
        """Return list of DNS name for that add-on."""
        return [f"{self.hostname}.{DNS_SUFFIX}"]

    @property
    def options(self) -> Dict[str, Any]:
        """Return options with local changes."""
        return {**self.data[ATTR_OPTIONS], **self.persist[ATTR_OPTIONS]}

    @options.setter
    def options(self, value: Optional[Dict[str, Any]]) -> None:
        """Store user add-on options."""
        self.persist[ATTR_OPTIONS] = {} if value is None else deepcopy(value)

    @property
    def boot(self) -> bool:
        """Return boot config with prio local settings."""
        return self.persist.get(ATTR_BOOT, super().boot)

    @boot.setter
    def boot(self, value: bool) -> None:
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
        self.persist[ATTR_WATCHDOG] = value

    @property
    def uuid(self) -> str:
        """Return an API token for this add-on."""
        return self.persist[ATTR_UUID]

    @property
    def supervisor_token(self) -> Optional[str]:
        """Return access token for Supervisor API."""
        return self.persist.get(ATTR_ACCESS_TOKEN)

    @property
    def ingress_token(self) -> Optional[str]:
        """Return access token for Supervisor API."""
        return self.persist.get(ATTR_INGRESS_TOKEN)

    @property
    def ingress_entry(self) -> Optional[str]:
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
    def ports(self) -> Optional[Dict[str, Optional[int]]]:
        """Return ports of add-on."""
        return self.persist.get(ATTR_NETWORK, super().ports)

    @ports.setter
    def ports(self, value: Optional[Dict[str, Optional[int]]]) -> None:
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
    def ingress_url(self) -> Optional[str]:
        """Return URL to ingress url."""
        if not self.with_ingress:
            return None

        url = f"/api/hassio_ingress/{self.ingress_token}/"
        if ATTR_INGRESS_ENTRY in self.data:
            return f"{url}{self.data[ATTR_INGRESS_ENTRY]}"
        return url

    @property
    def webui(self) -> Optional[str]:
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
    def ingress_port(self) -> Optional[int]:
        """Return Ingress port."""
        if not self.with_ingress:
            return None

        port = self.data[ATTR_INGRESS_PORT]
        if port == 0:
            return self.sys_ingress.get_dynamic_port(self.slug)
        return port

    @property
    def ingress_panel(self) -> Optional[bool]:
        """Return True if the add-on access support ingress."""
        return self.persist[ATTR_INGRESS_PANEL]

    @ingress_panel.setter
    def ingress_panel(self, value: bool) -> None:
        """Return True if the add-on access support ingress."""
        self.persist[ATTR_INGRESS_PANEL] = value

    @property
    def audio_output(self) -> Optional[str]:
        """Return a pulse profile for output or None."""
        if not self.with_audio:
            return None

        # Fallback with old audio settings
        # Remove after 210
        output_data = self.persist.get(ATTR_AUDIO_OUTPUT)
        if output_data and RE_OLD_AUDIO.fullmatch(output_data):
            return None
        return output_data

    @audio_output.setter
    def audio_output(self, value: Optional[str]):
        """Set audio output profile settings."""
        self.persist[ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self) -> Optional[str]:
        """Return pulse profile for input or None."""
        if not self.with_audio:
            return None

        # Fallback with old audio settings
        # Remove after 210
        input_data = self.persist.get(ATTR_AUDIO_INPUT)
        if input_data and RE_OLD_AUDIO.fullmatch(input_data):
            return None
        return input_data

    @audio_input.setter
    def audio_input(self, value: Optional[str]) -> None:
        """Set audio input settings."""
        self.persist[ATTR_AUDIO_INPUT] = value

    @property
    def image(self) -> Optional[str]:
        """Return image name of add-on."""
        return self.persist.get(ATTR_IMAGE)

    @property
    def need_build(self) -> bool:
        """Return True if this  add-on need a local build."""
        return ATTR_IMAGE not in self.data

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
        t_port = application.group("t_port")
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
            async with self.sys_websession_ssl.get(
                url, timeout=WATCHDOG_TIMEOUT
            ) as req:
                if req.status < 300:
                    return True
        except (asyncio.TimeoutError, aiohttp.ClientError):
            pass

        return False

    async def write_options(self) -> None:
        """Return True if add-on options is written to data."""
        schema = self.schema
        options = self.options

        # Update secrets for validation
        await self.sys_homeassistant.secrets.reload()

        try:
            options = schema(options)
            write_json_file(self.path_options, options)
        except vol.Invalid as ex:
            _LOGGER.error(
                "Add-on %s has invalid options: %s",
                self.slug,
                humanize_error(options, ex),
            )
        except JsonFileError:
            _LOGGER.error("Add-on %s can't write options", self.slug)
        else:
            _LOGGER.debug("Add-on %s write options: %s", self.slug, options)
            return

        raise AddonConfigurationError()

    async def remove_data(self) -> None:
        """Remove add-on data."""
        if not self.path_data.is_dir():
            return

        _LOGGER.info("Remove add-on data folder %s", self.path_data)
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
            with self.path_pulse.open("w") as config_file:
                config_file.write(pulse_config)
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
        options = {**self.persist[ATTR_OPTIONS], **default_options}

        # create voluptuous
        new_schema = vol.Schema(
            vol.All(dict, validate_options(self.coresys, new_raw_schema))
        )

        # validate
        try:
            new_schema(options)
        except vol.Invalid:
            _LOGGER.warning("Add-on %s new schema is not compatible", self.slug)
            return False
        return True

    async def start(self) -> None:
        """Set options and start add-on."""
        if await self.instance.is_running():
            _LOGGER.warning("%s already running!", self.slug)
            return

        # Access Token
        self.persist[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        self.save_persist()

        # Options
        await self.write_options()

        # Sound
        if self.with_audio:
            self.write_pulse()

        # Start Add-on
        try:
            await self.instance.run()
        except DockerAPIError as err:
            self.state = AddonState.ERROR
            raise AddonsError(err) from None
        else:
            self.state = AddonState.STARTED

    async def stop(self) -> None:
        """Stop add-on."""
        try:
            return await self.instance.stop()
        except DockerAPIError as err:
            self.state = AddonState.ERROR
            raise AddonsError() from err
        else:
            self.state = AddonState.STOPPED

    async def restart(self) -> None:
        """Restart add-on."""
        with suppress(AddonsError):
            await self.stop()
        await self.start()

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
        except DockerAPIError as err:
            raise AddonsError() from err

    async def write_stdin(self, data) -> None:
        """Write data to add-on stdin.

        Return a coroutine.
        """
        if not self.with_stdin:
            _LOGGER.error("Add-on %s does not support writing to stdin!", self.slug)
            raise AddonsNotSupportedError()

        try:
            return await self.instance.write_stdin(data)
        except DockerAPIError as err:
            raise AddonsError() from err

    async def snapshot(self, tar_file: tarfile.TarFile) -> None:
        """Snapshot state of an add-on."""
        with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
            temp_path = Path(temp)

            # store local image
            if self.need_build:
                try:
                    await self.instance.export_image(temp_path.joinpath("image.tar"))
                except DockerAPIError as err:
                    raise AddonsError() from err

            data = {
                ATTR_USER: self.persist,
                ATTR_SYSTEM: self.data,
                ATTR_VERSION: self.version,
                ATTR_STATE: self.state,
            }

            # Store local configs/state
            try:
                write_json_file(temp_path.joinpath("addon.json"), data)
            except JsonFileError as err:
                _LOGGER.error("Can't save meta for %s", self.slug)
                raise AddonsError() from err

            # Store AppArmor Profile
            if self.sys_host.apparmor.exists(self.slug):
                profile = temp_path.joinpath("apparmor.txt")
                try:
                    self.sys_host.apparmor.backup_profile(self.slug, profile)
                except HostAppArmorError as err:
                    _LOGGER.error("Can't backup AppArmor profile")
                    raise AddonsError() from err

            # write into tarfile
            def _write_tarfile():
                """Write tar inside loop."""
                with tar_file as snapshot:
                    # Snapshot system

                    snapshot.add(temp, arcname=".")

                    # Snapshot data
                    atomic_contents_add(
                        snapshot,
                        self.path_data,
                        excludes=self.snapshot_exclude,
                        arcname="data",
                    )

            try:
                _LOGGER.info("Build snapshot for add-on %s", self.slug)
                await self.sys_run_in_executor(_write_tarfile)
            except (tarfile.TarError, OSError) as err:
                _LOGGER.error("Can't write tarfile %s: %s", tar_file, err)
                raise AddonsError() from err

        _LOGGER.info("Finish snapshot for addon %s", self.slug)

    async def restore(self, tar_file: tarfile.TarFile) -> None:
        """Restore state of an add-on."""
        with TemporaryDirectory(dir=self.sys_config.path_tmp) as temp:
            # extract snapshot
            def _extract_tarfile():
                """Extract tar snapshot."""
                with tar_file as snapshot:
                    snapshot.extractall(path=Path(temp), members=secure_path(snapshot))

            try:
                await self.sys_run_in_executor(_extract_tarfile)
            except tarfile.TarError as err:
                _LOGGER.error("Can't read tarfile %s: %s", tar_file, err)
                raise AddonsError() from err

            # Read snapshot data
            try:
                data = read_json_file(Path(temp, "addon.json"))
            except JsonFileError as err:
                raise AddonsError() from err

            # Validate
            try:
                data = SCHEMA_ADDON_SNAPSHOT(data)
            except vol.Invalid as err:
                _LOGGER.error(
                    "Can't validate %s, snapshot data: %s",
                    self.slug,
                    humanize_error(data, err),
                )
                raise AddonsError() from err

            # If available
            if not self._available(data[ATTR_SYSTEM]):
                _LOGGER.error("Add-on %s is not available for this platform", self.slug)
                raise AddonsNotSupportedError()

            # Restore local add-on information
            _LOGGER.info("Restore config for addon %s", self.slug)
            restore_image = self._image(data[ATTR_SYSTEM])
            self.sys_addons.data.restore(
                self.slug, data[ATTR_USER], data[ATTR_SYSTEM], restore_image
            )

            # Check version / restore image
            version = data[ATTR_VERSION]
            if not await self.instance.exists():
                _LOGGER.info("Restore/Install image for addon %s", self.slug)

                image_file = Path(temp, "image.tar")
                if image_file.is_file():
                    with suppress(DockerAPIError):
                        await self.instance.import_image(image_file)
                else:
                    with suppress(DockerAPIError):
                        await self.instance.install(version, restore_image)
                        await self.instance.cleanup()
            elif self.instance.version != version or self.legacy:
                _LOGGER.info("Restore/Update image for addon %s", self.slug)
                with suppress(DockerAPIError):
                    await self.instance.update(version, restore_image)
            else:
                with suppress(DockerAPIError):
                    await self.instance.stop()

            # Restore data
            def _restore_data():
                """Restore data."""
                shutil.copytree(Path(temp, "data"), self.path_data, symlinks=True)

            _LOGGER.info("Restore data for addon %s", self.slug)
            if self.path_data.is_dir():
                await remove_data(self.path_data)
            try:
                await self.sys_run_in_executor(_restore_data)
            except shutil.Error as err:
                _LOGGER.error("Can't restore origin data: %s", err)
                raise AddonsError() from err

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

            # Run add-on
            if data[ATTR_STATE] == AddonState.STARTED:
                return await self.start()

        _LOGGER.info("Finish restore for add-on %s", self.slug)
