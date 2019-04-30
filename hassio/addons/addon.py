"""Init file for Hass.io add-ons."""
from contextlib import suppress
from copy import deepcopy
from ipaddress import IPv4Address, ip_address
import logging
from pathlib import Path, PurePath
import re
import secrets
import shutil
import tarfile
from tempfile import TemporaryDirectory
from typing import Any, Awaitable, Dict, Optional

import voluptuous as vol
from voluptuous.humanize import humanize_error

from ..const import (
    ATTR_ACCESS_TOKEN,
    ATTR_APPARMOR,
    ATTR_ARCH,
    ATTR_AUDIO,
    ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT,
    ATTR_AUTH_API,
    ATTR_AUTO_UART,
    ATTR_AUTO_UPDATE,
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
    ATTR_INGRESS_ENTRY,
    ATTR_INGRESS_PORT,
    ATTR_INGRESS_TOKEN,
    ATTR_INGRESS_PANEL,
    ATTR_PANEL_ADMIN,
    ATTR_PANEL_ICON,
    ATTR_PANEL_TITLE,
    ATTR_KERNEL_MODULES,
    ATTR_LEGACY,
    ATTR_LOCATON,
    ATTR_MACHINE,
    ATTR_MAP,
    ATTR_NAME,
    ATTR_NETWORK,
    ATTR_OPTIONS,
    ATTR_PORTS,
    ATTR_PORTS_DESCRIPTION,
    ATTR_PRIVILEGED,
    ATTR_PROTECTED,
    ATTR_REPOSITORY,
    ATTR_SCHEMA,
    ATTR_SERVICES,
    ATTR_SLUG,
    ATTR_STARTUP,
    ATTR_STATE,
    ATTR_STDIN,
    ATTR_SYSTEM,
    ATTR_TIMEOUT,
    ATTR_TMPFS,
    ATTR_URL,
    ATTR_USER,
    ATTR_UUID,
    ATTR_VERSION,
    ATTR_WEBUI,
    SECURITY_DEFAULT,
    SECURITY_DISABLE,
    SECURITY_PROFILE,
    STATE_NONE,
    STATE_STARTED,
    STATE_STOPPED,
)
from ..coresys import CoreSys
from ..docker.addon import DockerAddon
from ..docker.stats import DockerStats
from ..exceptions import (
    AddonsError,
    AddonsNotSupportedError,
    DockerAPIError,
    HostAppArmorError,
    JsonFileError,
)
from ..utils.apparmor import adjust_profile
from ..utils.json import read_json_file, write_json_file
from .utils import check_installed, remove_data
from .validate import (
    MACHINE_ALL,
    RE_SERVICE,
    RE_VOLUME,
    SCHEMA_ADDON_SNAPSHOT,
    validate_options,
)
from .model import AddonModel

_LOGGER = logging.getLogger(__name__)

RE_WEBUI = re.compile(
    r"^(?:(?P<s_prefix>https?)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:\[PORT:(?P<t_port>\d+)\](?P<s_suffix>.*)$")


class Addon(AddonModel):
    """Hold data for add-on inside Hass.io."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.instance: DockerAddon = DockerAddon(coresys, slug)
        self.slug: str = slug

    async def load(self) -> None:
        """Async initialize of object."""
        if not self.is_installed:
            return
        with suppress(DockerAPIError):
            await self.instance.attach()

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP of Add-on instance."""
        if not self.is_installed:
            return ip_address("0.0.0.0")
        return self.instance.ip_address

    @property
    def data(self) -> Dict[str, Any]:
        """Return add-on data/config."""
        return self.sys_addons.data.system[self.slug]

    @property
    def data_store(self) -> Dict[str, Any]:
        """Return add-on data from store."""
        return self.sys_store.data.addons.get(self.slug, self.data)

    @property
    def data_user(self) -> Dict[str, Any]:
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
    def version_installed(self) -> Optional[str]:
        """Return installed version."""
        return self.data_user[ATTR_VERSION]

    @property
    def options(self) -> Dict[str, Any]:
        """Return options with local changes."""
        return {
            **self.data[ATTR_OPTIONS],
            **self.data_user[ATTR_OPTIONS]
        }

    @options.setter
    def options(self, value: Optional[Dict[str, Any]]):
        """Store user add-on options."""
        if value is None:
            self.data_user[ATTR_OPTIONS] = {}
        else:
            self.data_user[ATTR_OPTIONS] = deepcopy(value)

    @property
    def boot(self) -> bool:
        """Return boot config with prio local settings."""
        return self.data_user.get(ATTR_BOOT, super().boot)

    @boot.setter
    def boot(self, value: bool):
        """Store user boot options."""
        self.data_user[ATTR_BOOT] = value

    @property
    def auto_update(self) -> bool:
        """Return if auto update is enable."""
        return self.data_user.get(ATTR_AUTO_UPDATE, super().auto_update)

    @auto_update.setter
    def auto_update(self, value: bool):
        """Set auto update."""
        self.data_user[ATTR_AUTO_UPDATE] = value

    @property
    def uuid(self) -> str:
        """Return an API token for this add-on."""
        return self.data_user[ATTR_UUID]

    @property
    def hassio_token(self) -> Optional[str]:
        """Return access token for Hass.io API."""
        return self.data_user.get(ATTR_ACCESS_TOKEN)

    @property
    def ingress_token(self) -> Optional[str]:
        """Return access token for Hass.io API."""
        return self.data_user.get(ATTR_INGRESS_TOKEN)

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
        return self.data_user[ATTR_PROTECTED]

    @protected.setter
    def protected(self, value: bool):
        """Set add-on in protected mode."""
        self.data_user[ATTR_PROTECTED] = value

    @property
    def ports(self) -> Optional[Dict[str, Optional[int]]]:
        """Return ports of add-on."""
        return self.data_user.get(ATTR_NETWORK, super().ports)

    @ports.setter
    def ports(self, value: Optional[Dict[str, Optional[int]]]):
        """Set custom ports of add-on."""
        if value is None:
            self.data_user.pop(ATTR_NETWORK, None)
            return

        # Secure map ports to value
        new_ports = {}
        for container_port, host_port in value.items():
            if container_port in self.data.get(ATTR_PORTS, {}):
                new_ports[container_port] = host_port

        self.data_user[ATTR_NETWORK] = new_ports

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
        t_port = webui.group('t_port')
        t_proto = webui.group('t_proto')
        s_prefix = webui.group('s_prefix') or ""
        s_suffix = webui.group('s_suffix') or ""

        # search host port for this docker port
        if self.ports is None:
            port = t_port
        else:
            port = self.ports.get(f"{t_port}/tcp", t_port)

        # for interface config or port lists
        if isinstance(port, (tuple, list)):
            port = port[-1]

        # lookup the correct protocol from config
        if t_proto:
            proto = 'https' if self.options[t_proto] else 'http'
        else:
            proto = s_prefix

        return f"{proto}://[HOST]:{port}{s_suffix}"

    @property
    def ingress_port(self) -> Optional[int]:
        """Return Ingress port."""
        if not self.with_ingress:
            return None

        port = super().ingress_port
        if port == 0:
            return self.sys_ingress.get_dynamic_port(self.slug)
        return port

    @property
    def ingress_panel(self) -> Optional[bool]:
        """Return True if the add-on access support ingress."""
        return self.data_user[ATTR_INGRESS_PANEL]

    @ingress_panel.setter
    def ingress_panel(self, value: bool):
        """Return True if the add-on access support ingress."""
        self.data_user[ATTR_INGRESS_PANEL] = value

    @property
    def audio_output(self) -> Optional[str]:
        """Return ALSA config for output or None."""
        if not self.with_audio:
            return None
        return self.data_user.get(ATTR_AUDIO_OUTPUT, self.sys_host.alsa.default.output)

    @audio_output.setter
    def audio_output(self, value: Optional[str]):
        """Set/reset audio output settings."""
        if value is None:
            self.data_user.pop(ATTR_AUDIO_OUTPUT, None)
        else:
            self.data_user[ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self) -> Optional[str]:
        """Return ALSA config for input or None."""
        if not self.with_audio:
            return None
        return self.data_user.get(ATTR_AUDIO_INPUT, self.sys_host.alsa.default.input)

    @audio_input.setter
    def audio_input(self, value: Optional[str]):
        """Set/reset audio input settings."""
        if value is None:
            self.data_user.pop(ATTR_AUDIO_INPUT, None)
        else:
            self.data_user[ATTR_AUDIO_INPUT] = value

    @property
    def image(self):
        """Return image name of add-on."""
        return self.data_user.get(ATTR_IMAGE)

    @property
    def image_next(self):
        """Return image name for install/update."""
        return self._image(self.data_store)

    @property
    def need_build(self):
        """Return True if this  add-on need a local build."""
        return ATTR_IMAGE not in self.data_store

    @property
    def path_data(self):
        """Return add-on data path inside Supervisor."""
        return Path(self.sys_config.path_addons_data, self.slug)

    @property
    def path_extern_data(self):
        """Return add-on data path external for Docker."""
        return PurePath(self.sys_config.path_extern_addons_data, self.slug)

    @property
    def path_options(self):
        """Return path to add-on options."""
        return Path(self.path_data, "options.json")

    @property
    def path_asound(self):
        """Return path to asound config."""
        return Path(self.sys_config.path_tmp, f"{self.slug}_asound")

    @property
    def path_extern_asound(self):
        """Return path to asound config for Docker."""
        return Path(self.sys_config.path_extern_tmp, f"{self.slug}_asound")

    def save_data(self):
        """Save data of add-on."""
        self.sys_addons.data.save_data()

    def write_options(self):
        """Return True if add-on options is written to data."""
        schema = self.schema
        options = self.options

        try:
            schema(options)
            write_json_file(self.path_options, options)
        except vol.Invalid as ex:
            _LOGGER.error("Add-on %s have wrong options: %s", self.slug,
                          humanize_error(options, ex))
        except JsonFileError:
            _LOGGER.error("Add-on %s can't write options", self.slug)
        else:
            return True

        return False

    def remove_discovery(self):
        """Remove all discovery message from add-on."""
        for message in self.sys_discovery.list_messages:
            if message.addon != self.slug:
                continue
            self.sys_discovery.remove(message)

    def write_asound(self):
        """Write asound config to file and return True on success."""
        asound_config = self.sys_host.alsa.asound(
            alsa_input=self.audio_input, alsa_output=self.audio_output)

        try:
            with self.path_asound.open('w') as config_file:
                config_file.write(asound_config)
        except OSError as err:
            _LOGGER.error("Add-on %s can't write asound: %s", self.slug, err)
            return False

        return True

    async def _install_apparmor(self) -> None:
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
            profile_file = Path(tmp_folder, 'apparmor.txt')

            adjust_profile(self.slug, self.path_apparmor, profile_file)
            await self.sys_host.apparmor.load_profile(self.slug, profile_file)

    def test_update_schema(self) -> bool:
        """Check if the existing configuration is valid after update."""
        # load next schema
        new_raw_schema = self.data_store[ATTR_SCHEMA]
        default_options = self.data_store[ATTR_OPTIONS]

        # if disabled
        if isinstance(new_raw_schema, bool):
            return True

        # merge options
        options = {
            **self.data_user[ATTR_OPTIONS],
            **default_options,
        }

        # create voluptuous
        new_schema = \
            vol.Schema(vol.All(dict, validate_options(new_raw_schema)))

        # validate
        try:
            new_schema(options)
        except vol.Invalid:
            _LOGGER.warning("Add-on %s new schema is not compatible", self.slug)
            return False
        return True

    async def install(self) -> None:
        """Install an add-on."""
        if not self.available:
            _LOGGER.error(
                "Add-on %s not supported on %s with %s architecture",
                self.slug, self.sys_machine, self.sys_arch.supported)
            raise AddonsNotSupportedError()

        if self.is_installed:
            _LOGGER.warning("Add-on %s is already installed", self.slug)
            return

        if not self.path_data.is_dir():
            _LOGGER.info(
                "Create Home Assistant add-on data folder %s", self.path_data)
            self.path_data.mkdir()

        # Setup/Fix AppArmor profile
        await self._install_apparmor()

        try:
            await self.instance.install(self.latest_version, self.image_next)
        except DockerAPIError:
            raise AddonsError() from None
        else:
            self._set_install(self.image_next, self.latest_version)

    async def uninstall(self) -> None:
        """Remove an add-on."""
        try:
            await self.instance.remove()
        except DockerAPIError:
            raise AddonsError() from None

        if self.path_data.is_dir():
            _LOGGER.info(
                "Remove Home Assistant add-on data folder %s", self.path_data)
            await remove_data(self.path_data)

        # Cleanup audio settings
        if self.path_asound.exists():
            with suppress(OSError):
                self.path_asound.unlink()

        # Cleanup AppArmor profile
        if self.sys_host.apparmor.exists(self.slug):
            with suppress(HostAppArmorError):
                await self.sys_host.apparmor.remove_profile(self.slug)

        # Cleanup internal data
        self.remove_discovery()
        self._set_uninstall()

    async def state(self) -> str:
        """Return running state of add-on."""
        if not self.is_installed:
            return STATE_NONE

        if await self.instance.is_running():
            return STATE_STARTED
        return STATE_STOPPED

    async def start(self) -> None:
        """Set options and start add-on."""
        if await self.instance.is_running():
            _LOGGER.warning("%s already running!", self.slug)
            return

        # Access Token
        self._data.user[self.slug][ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        self.save_data()

        # Options
        if not self.write_options():
            raise AddonsError()

        # Sound
        if self.with_audio and not self.write_asound():
            raise AddonsError()

        try:
            await self.instance.run()
        except DockerAPIError:
            raise AddonsError() from None

    async def stop(self) -> None:
        """Stop add-on."""
        try:
            return await self.instance.stop()
        except DockerAPIError:
            raise AddonsError() from None

    async def update(self) -> None:
        """Update add-on."""
        if self.latest_version == self.version_installed:
            _LOGGER.warning("No update available for add-on %s", self.slug)
            return

        # Check if available, Maybe something have changed
        if not self.available:
            _LOGGER.error(
                "Add-on %s not supported on %s with %s architecture",
                self.slug, self.sys_machine, self.sys_arch.supported)
            raise AddonsNotSupportedError()

        # Update instance
        last_state = await self.state()
        try:
            await self.instance.update(self.latest_version, self.image_next)
        except DockerAPIError:
            raise AddonsError() from None
        self._set_update(self.image_next, self.latest_version)

        # Setup/Fix AppArmor profile
        await self._install_apparmor()

        # restore state
        if last_state == STATE_STARTED:
            await self.start()

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

    async def stats(self) -> DockerStats:
        """Return stats of container."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise AddonsError() from None

    async def rebuild(self) -> None:
        """Perform a rebuild of local build add-on."""
        last_state = await self.state()

        if not self.need_build:
            _LOGGER.error("Can't rebuild a image based add-on")
            raise AddonsNotSupportedError()
        if self.version_installed != self.latest_version:
            _LOGGER.error("Version changed, use Update instead Rebuild")
            raise AddonsError()

        # remove docker container but not addon config
        try:
            await self.instance.remove()
            await self.instance.install(self.version_installed)
        except DockerAPIError:
            raise AddonsError() from None
        else:
            self._set_update(self.image, self.version_installed)

        # restore state
        if last_state == STATE_STARTED:
            await self.start()

    async def write_stdin(self, data):
        """Write data to add-on stdin.

        Return a coroutine.
        """
        if not self.with_stdin:
            _LOGGER.error("Add-on don't support write to stdin!")
            raise AddonsNotSupportedError()

        try:
            return await self.instance.write_stdin(data)
        except DockerAPIError:
            raise AddonsError() from None

    async def snapshot(self, tar_file: tarfile.TarFile) -> None:
        """Snapshot state of an add-on."""
        with TemporaryDirectory(dir=str(self.sys_config.path_tmp)) as temp:
            # store local image
            if self.need_build:
                try:
                    await self.instance.export_image(Path(temp, 'image.tar'))
                except DockerAPIError:
                    raise AddonsError() from None

            data = {
                ATTR_USER: self.data_user,
                ATTR_SYSTEM: self.data,
                ATTR_VERSION: self.version_installed,
                ATTR_STATE: await self.state(),
            }

            # Store local configs/state
            try:
                write_json_file(Path(temp, 'addon.json'), data)
            except JsonFileError:
                _LOGGER.error("Can't save meta for %s", self.slug)
                raise AddonsError() from None

            # Store AppArmor Profile
            if self.sys_host.apparmor.exists(self.slug):
                profile = Path(temp, 'apparmor.txt')
                try:
                    self.sys_host.apparmor.backup_profile(self.slug, profile)
                except HostAppArmorError:
                    _LOGGER.error("Can't backup AppArmor profile")
                    raise AddonsError() from None

            # write into tarfile
            def _write_tarfile():
                """Write tar inside loop."""
                with tar_file as snapshot:
                    snapshot.add(temp, arcname=".")
                    snapshot.add(self.path_data, arcname="data")

            try:
                _LOGGER.info("Build snapshot for add-on %s", self.slug)
                await self.sys_run_in_executor(_write_tarfile)
            except (tarfile.TarError, OSError) as err:
                _LOGGER.error("Can't write tarfile %s: %s", tar_file, err)
                raise AddonsError() from None

        _LOGGER.info("Finish snapshot for addon %s", self.slug)

    async def restore(self, tar_file: tarfile.TarFile) -> None:
        """Restore state of an add-on."""
        with TemporaryDirectory(dir=str(self.sys_config.path_tmp)) as temp:
            # extract snapshot
            def _extract_tarfile():
                """Extract tar snapshot."""
                with tar_file as snapshot:
                    snapshot.extractall(path=Path(temp))

            try:
                await self.sys_run_in_executor(_extract_tarfile)
            except tarfile.TarError as err:
                _LOGGER.error("Can't read tarfile %s: %s", tar_file, err)
                raise AddonsError() from None

            # Read snapshot data
            try:
                data = read_json_file(Path(temp, 'addon.json'))
            except JsonFileError:
                raise AddonsError() from None

            # Validate
            try:
                data = SCHEMA_ADDON_SNAPSHOT(data)
            except vol.Invalid as err:
                _LOGGER.error("Can't validate %s, snapshot data: %s",
                              self.slug, humanize_error(data, err))
                raise AddonsError() from None

            # Restore local add-on informations
            _LOGGER.info("Restore config for addon %s", self.slug)
            restore_image = self._image(data[ATTR_SYSTEM])
            self._restore_data(data[ATTR_USER], data[ATTR_SYSTEM], restore_image)

            # Check version / restore image
            version = data[ATTR_VERSION]
            if not await self.instance.exists():
                _LOGGER.info("Restore/Install image for addon %s", self.slug)

                image_file = Path(temp, 'image.tar')
                if image_file.is_file():
                    with suppress(DockerAPIError):
                        await self.instance.import_image(image_file, version)
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
                shutil.copytree(str(Path(temp, "data")), str(self.path_data))

            _LOGGER.info("Restore data for addon %s", self.slug)
            if self.path_data.is_dir():
                await remove_data(self.path_data)
            try:
                await self.sys_run_in_executor(_restore_data)
            except shutil.Error as err:
                _LOGGER.error("Can't restore origin data: %s", err)
                raise AddonsError() from None

            # Restore AppArmor
            profile_file = Path(temp, 'apparmor.txt')
            if profile_file.exists():
                try:
                    await self.sys_host.apparmor.load_profile(
                        self.slug, profile_file)
                except HostAppArmorError:
                    _LOGGER.error("Can't restore AppArmor profile")
                    raise AddonsError() from None

            # Run add-on
            if data[ATTR_STATE] == STATE_STARTED:
                return await self.start()

        _LOGGER.info("Finish restore for add-on %s", self.slug)
