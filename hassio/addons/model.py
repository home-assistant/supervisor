"""Init file for Hass.io add-ons."""
from contextlib import suppress
from copy import deepcopy
from distutils.version import StrictVersion
from ipaddress import IPv4Address, ip_address
import logging
from pathlib import Path, PurePath
import re
import secrets
import shutil
import tarfile
from tempfile import TemporaryDirectory
from typing import Any, Awaitable, Dict, Optional, List

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
from ..coresys import CoreSys, CoreSysAttributes
from ..docker.addon import DockerAddon
from ..docker.stats import DockerStats
from ..exceptions import (
    AddonsError,
    AddonsNotSupportedError,
    DockerAPIError,
    HostAppArmorError,
    JsonFileError,
)
from .validate import RE_SERVICE


class AddonModel(CoreSysAttributes):
    """Add-on Data layout."""

    @property
    def data(self) -> Dict[str, Any]:
        """Return Add-on config/data."""
        raise NotImplementedError()

    @property
    def slug(self) -> str:
        """Return slug/id of add-on."""
        raise NotImplementedError()

    @property
    def is_installed(self) -> bool:
        """Return True if an add-on is installed."""
        raise NotImplementedError()

    @property
    def is_detached(self) -> bool:
        """Return True if add-on is detached."""
        raise NotImplementedError()

    @property
    def available(self) -> bool:
        """Return True if this add-on is available on this platform."""
        raise NotImplementedError()

    @property
    def options(self) -> Dict[str, Any]:
        """Return options with local changes."""
        return self.data[ATTR_OPTIONS]

    @property
    def boot(self) -> bool:
        """Return boot config with prio local settings."""
        return self.data[ATTR_BOOT]

    def auto_update(self) -> Optional[bool]:
        """Return if auto update is enable."""
        return None

    @property
    def name(self) -> str:
        """Return name of add-on."""
        return self.data[ATTR_NAME]

    @property
    def timeout(self) -> int:
        """Return timeout of addon for docker stop."""
        return self.data[ATTR_TIMEOUT]

    @property
    def uuid(self) -> Optional[str]:
        """Return an API token for this add-on."""
        return None

    @property
    def hassio_token(self) -> Optional[str]:
        """Return access token for Hass.io API."""
        return None

    @property
    def ingress_token(self) -> Optional[str]:
        """Return access token for Hass.io API."""
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
        readme = Path(self.path_location, 'README.md')

        # If readme not exists
        if not readme.exists():
            return None

        # Return data
        with readme.open('r') as readme_file:
            return readme_file.read()

    @property
    def repository(self) -> str:
        """Return repository of add-on."""
        return self.data[ATTR_REPOSITORY]

    @property
    def latest_version(self) -> str:
        """Return version of add-on."""
        return self.data[ATTR_VERSION]

    @property
    def protected(self) -> bool:
        """Return if add-on is in protected mode."""
        return True

    @property
    def startup(self) -> Optional[str]:
        """Return startup type of add-on."""
        return self.data.get(ATTR_STARTUP)

    @property
    def services_role(self) -> Dict[str, str]:
        """Return dict of services with rights."""
        services_list = self.data.get(ATTR_SERVICES, [])

        services = {}
        for data in services_list:
            service = RE_SERVICE.match(data)
            services[service.group('service')] = service.group('rights')

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
        return None

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
    def devices(self) -> Optional[List[str]]:
        """Return devices of add-on."""
        return self.data.get(ATTR_DEVICES)

    @property
    def auto_uart(self) -> bool:
        """Return True if we should map all UART device."""
        return self.data[ATTR_AUTO_UART]

    @property
    def tmpfs(self) -> Optional[str]:
        """Return tmpfs of add-on."""
        return self.data.get(ATTR_TMPFS)

    @property
    def environment(self) -> Optional[Dict[str, str]]:
        """Return environment of add-on."""
        return self.data.get(ATTR_ENVIRONMENT)

    @property
    def privileged(self) -> List[str]:
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
        """Return True if the add-on access to Hass.io REASTful API."""
        return self.data[ATTR_HASSIO_API]

    @property
    def access_homeassistant_api(self) -> bool:
        """Return True if the add-on access to Home Assistant API proxy."""
        return self.data[ATTR_HOMEASSISTANT_API]

    @property
    def hassio_role(self) -> str:
        """Return Hass.io role for API."""
        return self.data[ATTR_HASSIO_ROLE]

    @property
    def with_stdin(self) -> bool:
        """Return True if the add-on access use stdin input."""
        return self.data[ATTR_STDIN]

    @property
    def with_ingress(self):
        """Return True if the add-on access support ingress."""
        return self._mesh[ATTR_INGRESS]

    @property
    def ingress_panel(self) -> Optional[bool]:
        """Return True if the add-on access support ingress."""
        if self.is_installed:
            return self._data.user[self._id][ATTR_INGRESS_PANEL]
        return None

    @ingress_panel.setter
    def ingress_panel(self, value: bool):
        """Return True if the add-on access support ingress."""
        self._data.user[self._id][ATTR_INGRESS_PANEL] = value

    @property
    def with_gpio(self):
        """Return True if the add-on access to GPIO interface."""
        return self._mesh[ATTR_GPIO]

    @property
    def with_kernel_modules(self):
        """Return True if the add-on access to kernel modules."""
        return self._mesh[ATTR_KERNEL_MODULES]

    @property
    def with_full_access(self):
        """Return True if the add-on want full access to hardware."""
        return self._mesh[ATTR_FULL_ACCESS]

    @property
    def with_devicetree(self):
        """Return True if the add-on read access to devicetree."""
        return self._mesh[ATTR_DEVICETREE]

    @property
    def access_auth_api(self):
        """Return True if the add-on access to login/auth backend."""
        return self._mesh[ATTR_AUTH_API]

    @property
    def with_audio(self):
        """Return True if the add-on access to audio."""
        return self._mesh[ATTR_AUDIO]

    @property
    def homeassistant_version(self) -> Optional[str]:
        """Return min Home Assistant version they needed by Add-on."""
        return self._mesh.get(ATTR_HOMEASSISTANT)

    @property
    def audio_output(self):
        """Return ALSA config for output or None."""
        if not self.with_audio:
            return None

        if self.is_installed and \
                ATTR_AUDIO_OUTPUT in self._data.user[self._id]:
            return self._data.user[self._id][ATTR_AUDIO_OUTPUT]
        return self.sys_host.alsa.default.output

    @audio_output.setter
    def audio_output(self, value):
        """Set/reset audio output settings."""
        if value is None:
            self._data.user[self._id].pop(ATTR_AUDIO_OUTPUT, None)
        else:
            self._data.user[self._id][ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self):
        """Return ALSA config for input or None."""
        if not self.with_audio:
            return None

        if self.is_installed and ATTR_AUDIO_INPUT in self._data.user[self._id]:
            return self._data.user[self._id][ATTR_AUDIO_INPUT]
        return self.sys_host.alsa.default.input

    @audio_input.setter
    def audio_input(self, value):
        """Set/reset audio input settings."""
        if value is None:
            self._data.user[self._id].pop(ATTR_AUDIO_INPUT, None)
        else:
            self._data.user[self._id][ATTR_AUDIO_INPUT] = value

    @property
    def url(self):
        """Return URL of add-on."""
        return self._mesh.get(ATTR_URL)

    @property
    def with_icon(self):
        """Return True if an icon exists."""
        return self.path_icon.exists()

    @property
    def with_logo(self):
        """Return True if a logo exists."""
        return self.path_logo.exists()

    @property
    def with_changelog(self):
        """Return True if a changelog exists."""
        return self.path_changelog.exists()

    @property
    def supported_arch(self):
        """Return list of supported arch."""
        return self._mesh[ATTR_ARCH]

    @property
    def supported_machine(self):
        """Return list of supported machine."""
        return self._mesh.get(ATTR_MACHINE) or MACHINE_ALL

    @property
    def image(self):
        """Return image name of add-on."""
        if self.is_installed:
            return self._data.user[self._id].get(ATTR_IMAGE)
        return self.image_next

    @property
    def image_next(self):
        """Return image name for install/update."""
        if self.is_detached:
            addon_data = self._data.system.get(self._id)
        else:
            addon_data = self._data.cache.get(self._id)
        return self._get_image(addon_data)

    def _get_image(self, addon_data) -> str:
        """Generate image name from data."""
        # Repository with Dockerhub images
        if ATTR_IMAGE in addon_data:
            arch = self.sys_arch.match(addon_data[ATTR_ARCH])
            return addon_data[ATTR_IMAGE].format(arch=arch)

        # local build
        return (f"{addon_data[ATTR_REPOSITORY]}/"
                f"{self.sys_arch.default}-"
                f"addon-{addon_data[ATTR_SLUG]}")

    @property
    def need_build(self):
        """Return True if this  add-on need a local build."""
        if self.is_detached:
            return ATTR_IMAGE not in self._data.system.get(self._id)
        return ATTR_IMAGE not in self._data.cache.get(self._id)

    @property
    def map_volumes(self):
        """Return a dict of {volume: policy} from add-on."""
        volumes = {}
        for volume in self._mesh[ATTR_MAP]:
            result = RE_VOLUME.match(volume)
            volumes[result.group(1)] = result.group(2) or 'ro'

        return volumes

    @property
    def path_data(self):
        """Return add-on data path inside Supervisor."""
        return Path(self.sys_config.path_addons_data, self._id)

    @property
    def path_extern_data(self):
        """Return add-on data path external for Docker."""
        return PurePath(self.sys_config.path_extern_addons_data, self._id)

    @property
    def path_options(self):
        """Return path to add-on options."""
        return Path(self.path_data, "options.json")

    @property
    def path_location(self):
        """Return path to this add-on."""
        return Path(self._mesh[ATTR_LOCATON])

    @property
    def path_icon(self):
        """Return path to add-on icon."""
        return Path(self.path_location, 'icon.png')

    @property
    def path_logo(self):
        """Return path to add-on logo."""
        return Path(self.path_location, 'logo.png')

    @property
    def path_changelog(self):
        """Return path to add-on changelog."""
        return Path(self.path_location, 'CHANGELOG.md')

    @property
    def path_apparmor(self):
        """Return path to custom AppArmor profile."""
        return Path(self.path_location, 'apparmor.txt')

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
            _LOGGER.error("Add-on %s have wrong options: %s", self._id,
                          humanize_error(options, ex))
        except JsonFileError:
            _LOGGER.error("Add-on %s can't write options", self._id)
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
            _LOGGER.error("Add-on %s can't write asound: %s", self._id, err)
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

    @property
    def schema(self) -> vol.Schema:
        """Create a schema for add-on options."""
        raw_schema = self._mesh[ATTR_SCHEMA]

        if isinstance(raw_schema, bool):
            return vol.Schema(dict)
        return vol.Schema(vol.All(dict, validate_options(raw_schema)))

    def test_update_schema(self) -> bool:
        """Check if the existing configuration is valid after update."""
        if not self.is_installed or self.is_detached:
            return True

        # load next schema
        new_raw_schema = self._data.cache[self._id][ATTR_SCHEMA]
        default_options = self._data.cache[self._id][ATTR_OPTIONS]

        # if disabled
        if isinstance(new_raw_schema, bool):
            return True

        # merge options
        options = {
            **self._data.user[self._id][ATTR_OPTIONS],
            **default_options,
        }

        # create voluptuous
        new_schema = \
            vol.Schema(vol.All(dict, validate_options(new_raw_schema)))

        # validate
        try:
            new_schema(options)
        except vol.Invalid:
            return False
        return True

    async def install(self) -> None:
        """Install an add-on."""
        if not self.available:
            _LOGGER.error(
                "Add-on %s not supported on %s with %s architecture",
                self._id, self.sys_machine, self.sys_arch.supported)
            raise AddonsNotSupportedError()

        if self.is_installed:
            _LOGGER.warning("Add-on %s is already installed", self._id)
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

    @check_installed
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

    @check_installed
    async def start(self) -> None:
        """Set options and start add-on."""
        if await self.instance.is_running():
            _LOGGER.warning("%s already running!", self.slug)
            return

        # Access Token
        self._data.user[self._id][ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
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

    @check_installed
    async def stop(self) -> None:
        """Stop add-on."""
        try:
            return await self.instance.stop()
        except DockerAPIError:
            raise AddonsError() from None

    @check_installed
    async def update(self) -> None:
        """Update add-on."""
        if self.latest_version == self.version_installed:
            _LOGGER.warning("No update available for add-on %s", self._id)
            return

        # Check if available, Maybe something have changed
        if not self.available:
            _LOGGER.error(
                "Add-on %s not supported on %s with %s architecture",
                self._id, self.sys_machine, self.sys_arch.supported)
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

    @check_installed
    async def restart(self) -> None:
        """Restart add-on."""
        with suppress(AddonsError):
            await self.stop()
        await self.start()

    @check_installed
    def logs(self) -> Awaitable[bytes]:
        """Return add-ons log output.

        Return a coroutine.
        """
        return self.instance.logs()

    @check_installed
    async def stats(self) -> DockerStats:
        """Return stats of container."""
        try:
            return await self.instance.stats()
        except DockerAPIError:
            raise AddonsError() from None

    @check_installed
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

    @check_installed
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

    @check_installed
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
                ATTR_USER: self._data.user.get(self._id, {}),
                ATTR_SYSTEM: self._data.system.get(self._id, {}),
                ATTR_VERSION: self.version_installed,
                ATTR_STATE: await self.state(),
            }

            # Store local configs/state
            try:
                write_json_file(Path(temp, 'addon.json'), data)
            except JsonFileError:
                _LOGGER.error("Can't save meta for %s", self._id)
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
                _LOGGER.info("Build snapshot for add-on %s", self._id)
                await self.sys_run_in_executor(_write_tarfile)
            except (tarfile.TarError, OSError) as err:
                _LOGGER.error("Can't write tarfile %s: %s", tar_file, err)
                raise AddonsError() from None

        _LOGGER.info("Finish snapshot for addon %s", self._id)

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
                              self._id, humanize_error(data, err))
                raise AddonsError() from None

            # Restore local add-on informations
            _LOGGER.info("Restore config for addon %s", self._id)
            restore_image = self._get_image(data[ATTR_SYSTEM])
            self._restore_data(data[ATTR_USER], data[ATTR_SYSTEM], restore_image)

            # Check version / restore image
            version = data[ATTR_VERSION]
            if not await self.instance.exists():
                _LOGGER.info("Restore/Install image for addon %s", self._id)

                image_file = Path(temp, 'image.tar')
                if image_file.is_file():
                    with suppress(DockerAPIError):
                        await self.instance.import_image(image_file, version)
                else:
                    with suppress(DockerAPIError):
                        await self.instance.install(version, restore_image)
                        await self.instance.cleanup()
            elif self.instance.version != version or self.legacy:
                _LOGGER.info("Restore/Update image for addon %s", self._id)
                with suppress(DockerAPIError):
                    await self.instance.update(version, restore_image)
            else:
                with suppress(DockerAPIError):
                    await self.instance.stop()

            # Restore data
            def _restore_data():
                """Restore data."""
                shutil.copytree(str(Path(temp, "data")), str(self.path_data))

            _LOGGER.info("Restore data for addon %s", self._id)
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

        _LOGGER.info("Finish restore for add-on %s", self._id)
