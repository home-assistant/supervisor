"""Init file for HassIO addons."""
from copy import deepcopy
import logging
import json
from pathlib import Path, PurePath
import re
import shutil
import tarfile
from tempfile import TemporaryDirectory

import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import (
    validate_options, SCHEMA_ADDON_SNAPSHOT, RE_VOLUME, RE_SERVICE)
from .utils import check_installed
from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_BOOT, ATTR_MAP,
    ATTR_OPTIONS, ATTR_PORTS, ATTR_SCHEMA, ATTR_IMAGE, ATTR_REPOSITORY,
    ATTR_URL, ATTR_ARCH, ATTR_LOCATON, ATTR_DEVICES, ATTR_ENVIRONMENT,
    ATTR_HOST_NETWORK, ATTR_TMPFS, ATTR_PRIVILEGED, ATTR_STARTUP, ATTR_UUID,
    STATE_STARTED, STATE_STOPPED, STATE_NONE, ATTR_USER, ATTR_SYSTEM,
    ATTR_STATE, ATTR_TIMEOUT, ATTR_AUTO_UPDATE, ATTR_NETWORK, ATTR_WEBUI,
    ATTR_HASSIO_API, ATTR_AUDIO, ATTR_AUDIO_OUTPUT, ATTR_AUDIO_INPUT,
    ATTR_GPIO, ATTR_HOMEASSISTANT_API, ATTR_STDIN, ATTR_LEGACY, ATTR_HOST_IPC,
    ATTR_HOST_DBUS, ATTR_AUTO_UART, ATTR_DISCOVERY, ATTR_SERVICES)
from ..coresys import CoreSysAttributes
from ..docker.addon import DockerAddon
from ..utils.json import write_json_file, read_json_file

_LOGGER = logging.getLogger(__name__)

RE_WEBUI = re.compile(
    r"^(?:(?P<s_prefix>https?)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:\[PORT:(?P<t_port>\d+)\](?P<s_suffix>.*)$")


class Addon(CoreSysAttributes):
    """Hold data for addon inside HassIO."""

    def __init__(self, coresys, slug):
        """Initialize data holder."""
        self.coresys = coresys
        self.instance = DockerAddon(coresys, slug)

        self._id = slug

    async def load(self):
        """Async initialize of object."""
        if self.is_installed:
            await self.instance.attach()

    @property
    def slug(self):
        """Return slug/id of addon."""
        return self._id

    @property
    def _mesh(self):
        """Return addon data from system or cache."""
        return self._data.system.get(self._id, self._data.cache.get(self._id))

    @property
    def _data(self):
        """Return addons data storage."""
        return self._addons.data

    @property
    def is_installed(self):
        """Return True if a addon is installed."""
        return self._id in self._data.system

    @property
    def is_detached(self):
        """Return True if addon is detached."""
        return self._id not in self._data.cache

    @property
    def version_installed(self):
        """Return installed version."""
        return self._data.user.get(self._id, {}).get(ATTR_VERSION)

    def _set_install(self, version):
        """Set addon as installed."""
        self._data.system[self._id] = deepcopy(self._data.cache[self._id])
        self._data.user[self._id] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: version,
        }
        self._data.save_data()

    def _set_uninstall(self):
        """Set addon as uninstalled."""
        self._data.system.pop(self._id, None)
        self._data.user.pop(self._id, None)
        self._data.save_data()

    def _set_update(self, version):
        """Update version of addon."""
        self._data.system[self._id] = deepcopy(self._data.cache[self._id])
        self._data.user[self._id][ATTR_VERSION] = version
        self._data.save_data()

    def _restore_data(self, user, system):
        """Restore data to addon."""
        self._data.user[self._id] = deepcopy(user)
        self._data.system[self._id] = deepcopy(system)
        self._data.save_data()

    @property
    def options(self):
        """Return options with local changes."""
        if self.is_installed:
            return {
                **self._data.system[self._id][ATTR_OPTIONS],
                **self._data.user[self._id][ATTR_OPTIONS]
            }
        return self._data.cache[self._id][ATTR_OPTIONS]

    @options.setter
    def options(self, value):
        """Store user addon options."""
        if value is None:
            self._data.user[self._id][ATTR_OPTIONS] = {}
        else:
            self._data.user[self._id][ATTR_OPTIONS] = deepcopy(value)

    @property
    def boot(self):
        """Return boot config with prio local settings."""
        if ATTR_BOOT in self._data.user.get(self._id, {}):
            return self._data.user[self._id][ATTR_BOOT]
        return self._mesh[ATTR_BOOT]

    @boot.setter
    def boot(self, value):
        """Store user boot options."""
        self._data.user[self._id][ATTR_BOOT] = value

    @property
    def auto_update(self):
        """Return if auto update is enable."""
        if ATTR_AUTO_UPDATE in self._data.user.get(self._id, {}):
            return self._data.user[self._id][ATTR_AUTO_UPDATE]
        return None

    @auto_update.setter
    def auto_update(self, value):
        """Set auto update."""
        self._data.user[self._id][ATTR_AUTO_UPDATE] = value

    @property
    def name(self):
        """Return name of addon."""
        return self._mesh[ATTR_NAME]

    @property
    def timeout(self):
        """Return timeout of addon for docker stop."""
        return self._mesh[ATTR_TIMEOUT]

    @property
    def uuid(self):
        """Return a API token for this add-on."""
        if self.is_installed:
            return self._data.user[self._id][ATTR_UUID]
        return None

    @property
    def description(self):
        """Return description of addon."""
        return self._mesh[ATTR_DESCRIPTON]

    @property
    def long_description(self):
        """Return README.md as long_description."""
        readme = Path(self.path_location, 'README.md')

        # If readme not exists
        if not readme.exists():
            return None

        # Return data
        with readme.open('r') as readme_file:
            return readme_file.read()

    @property
    def repository(self):
        """Return repository of addon."""
        return self._mesh[ATTR_REPOSITORY]

    @property
    def last_version(self):
        """Return version of addon."""
        if self._id in self._data.cache:
            return self._data.cache[self._id][ATTR_VERSION]
        return self.version_installed

    @property
    def startup(self):
        """Return startup type of addon."""
        return self._mesh.get(ATTR_STARTUP)

    @property
    def services(self):
        """Return dict of services with rights."""
        raw_services = self._mesh.get(ATTR_SERVICES)
        if not raw_services:
            return None

        formated_services = {}
        for data in raw_services:
            service = RE_SERVICE.match(data)
            formated_services[service.group('service')] = \
                service.group('rights') or 'ro'

        return formated_services

    @property
    def discovery(self):
        """Return list of discoverable components/platforms."""
        return self._mesh.get(ATTR_DISCOVERY)

    @property
    def ports(self):
        """Return ports of addon."""
        if self.host_network or ATTR_PORTS not in self._mesh:
            return None

        if not self.is_installed or \
                ATTR_NETWORK not in self._data.user[self._id]:
            return self._mesh[ATTR_PORTS]
        return self._data.user[self._id][ATTR_NETWORK]

    @ports.setter
    def ports(self, value):
        """Set custom ports of addon."""
        if value is None:
            self._data.user[self._id].pop(ATTR_NETWORK, None)
        else:
            new_ports = {}
            for container_port, host_port in value.items():
                if container_port in self._mesh.get(ATTR_PORTS, {}):
                    new_ports[container_port] = host_port

            self._data.user[self._id][ATTR_NETWORK] = new_ports

    @property
    def webui(self):
        """Return URL to webui or None."""
        if ATTR_WEBUI not in self._mesh:
            return None
        webui = RE_WEBUI.match(self._mesh[ATTR_WEBUI])

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
    def host_network(self):
        """Return True if addon run on host network."""
        return self._mesh[ATTR_HOST_NETWORK]

    @property
    def host_ipc(self):
        """Return True if addon run on host IPC namespace."""
        return self._mesh[ATTR_HOST_IPC]

    @property
    def host_dbus(self):
        """Return True if addon run on host DBUS."""
        return self._mesh[ATTR_HOST_DBUS]

    @property
    def devices(self):
        """Return devices of addon."""
        return self._mesh.get(ATTR_DEVICES)

    @property
    def auto_uart(self):
        """Return True if we should map all uart device."""
        return self._mesh.get(ATTR_AUTO_UART)

    @property
    def tmpfs(self):
        """Return tmpfs of addon."""
        return self._mesh.get(ATTR_TMPFS)

    @property
    def environment(self):
        """Return environment of addon."""
        return self._mesh.get(ATTR_ENVIRONMENT)

    @property
    def privileged(self):
        """Return list of privilege."""
        return self._mesh.get(ATTR_PRIVILEGED)

    @property
    def legacy(self):
        """Return if the add-on don't support hass labels."""
        return self._mesh.get(ATTR_LEGACY)

    @property
    def access_hassio_api(self):
        """Return True if the add-on access to hassio api."""
        return self._mesh[ATTR_HASSIO_API]

    @property
    def access_homeassistant_api(self):
        """Return True if the add-on access to Home-Assistant api proxy."""
        return self._mesh[ATTR_HOMEASSISTANT_API]

    @property
    def with_stdin(self):
        """Return True if the add-on access use stdin input."""
        return self._mesh[ATTR_STDIN]

    @property
    def with_gpio(self):
        """Return True if the add-on access to gpio interface."""
        return self._mesh[ATTR_GPIO]

    @property
    def with_audio(self):
        """Return True if the add-on access to audio."""
        return self._mesh[ATTR_AUDIO]

    @property
    def audio_output(self):
        """Return ALSA config for output or None."""
        if not self.with_audio:
            return None

        setting = self._config.audio_output
        if self.is_installed and \
                ATTR_AUDIO_OUTPUT in self._data.user[self._id]:
            setting = self._data.user[self._id][ATTR_AUDIO_OUTPUT]
        return setting

    @audio_output.setter
    def audio_output(self, value):
        """Set/remove custom audio output settings."""
        if value is None:
            self._data.user[self._id].pop(ATTR_AUDIO_OUTPUT, None)
        else:
            self._data.user[self._id][ATTR_AUDIO_OUTPUT] = value

    @property
    def audio_input(self):
        """Return ALSA config for input or None."""
        if not self.with_audio:
            return None

        setting = self._config.audio_input
        if self.is_installed and ATTR_AUDIO_INPUT in self._data.user[self._id]:
            setting = self._data.user[self._id][ATTR_AUDIO_INPUT]
        return setting

    @audio_input.setter
    def audio_input(self, value):
        """Set/remove custom audio input settings."""
        if value is None:
            self._data.user[self._id].pop(ATTR_AUDIO_INPUT, None)
        else:
            self._data.user[self._id][ATTR_AUDIO_INPUT] = value

    @property
    def url(self):
        """Return url of addon."""
        return self._mesh.get(ATTR_URL)

    @property
    def with_icon(self):
        """Return True if a icon exists."""
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
    def image(self):
        """Return image name of addon."""
        addon_data = self._mesh

        # Repository with dockerhub images
        if ATTR_IMAGE in addon_data:
            return addon_data[ATTR_IMAGE].format(arch=self._arch)

        # local build
        return "{}/{}-addon-{}".format(
            addon_data[ATTR_REPOSITORY], self._arch,
            addon_data[ATTR_SLUG])

    @property
    def need_build(self):
        """Return True if this  addon need a local build."""
        return ATTR_IMAGE not in self._mesh

    @property
    def map_volumes(self):
        """Return a dict of {volume: policy} from addon."""
        volumes = {}
        for volume in self._mesh[ATTR_MAP]:
            result = RE_VOLUME.match(volume)
            volumes[result.group(1)] = result.group(2) or 'ro'

        return volumes

    @property
    def path_data(self):
        """Return addon data path inside supervisor."""
        return Path(self._config.path_addons_data, self._id)

    @property
    def path_extern_data(self):
        """Return addon data path external for docker."""
        return PurePath(self._config.path_extern_addons_data, self._id)

    @property
    def path_options(self):
        """Return path to addons options."""
        return Path(self.path_data, "options.json")

    @property
    def path_location(self):
        """Return path to this addon."""
        return Path(self._mesh[ATTR_LOCATON])

    @property
    def path_icon(self):
        """Return path to addon icon."""
        return Path(self.path_location, 'icon.png')

    @property
    def path_logo(self):
        """Return path to addon logo."""
        return Path(self.path_location, 'logo.png')

    @property
    def path_changelog(self):
        """Return path to addon changelog."""
        return Path(self.path_location, 'CHANGELOG.md')

    def save_data(self):
        """Save data of addon."""
        self._addons.data.save_data()

    def write_options(self):
        """Return True if addon options is written to data."""
        schema = self.schema
        options = self.options

        try:
            schema(options)
            write_json_file(self.path_options, options)
        except vol.Invalid as ex:
            _LOGGER.error("Addon %s have wrong options: %s", self._id,
                          humanize_error(options, ex))
        except (OSError, json.JSONDecodeError) as err:
            _LOGGER.error("Addon %s can't write options: %s", self._id, err)
        else:
            return True

        return False

    @property
    def schema(self):
        """Create a schema for addon options."""
        raw_schema = self._mesh[ATTR_SCHEMA]

        if isinstance(raw_schema, bool):
            return vol.Schema(dict)
        return vol.Schema(vol.All(dict, validate_options(raw_schema)))

    def test_udpate_schema(self):
        """Check if the exists config valid after update."""
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

    async def install(self):
        """Install a addon."""
        if self._arch not in self.supported_arch:
            _LOGGER.error(
                "Addon %s not supported on %s", self._id, self._arch)
            return False

        if self.is_installed:
            _LOGGER.error("Addon %s is already installed", self._id)
            return False

        if not self.path_data.is_dir():
            _LOGGER.info(
                "Create Home-Assistant addon data folder %s", self.path_data)
            self.path_data.mkdir()

        if not await self.instance.install(self.last_version):
            return False

        self._set_install(self.last_version)
        return True

    @check_installed
    async def uninstall(self):
        """Remove a addon."""
        if not await self.instance.remove():
            return False

        if self.path_data.is_dir():
            _LOGGER.info(
                "Remove Home-Assistant addon data folder %s", self.path_data)
            shutil.rmtree(str(self.path_data))

        self._set_uninstall()
        return True

    async def state(self):
        """Return running state of addon."""
        if not self.is_installed:
            return STATE_NONE

        if await self.instance.is_running():
            return STATE_STARTED
        return STATE_STOPPED

    @check_installed
    async def start(self):
        """Set options and start addon."""
        if not self.write_options():
            return False

        return await self.instance.run()

    @check_installed
    def stop(self):
        """Stop addon.

        Return a coroutine.
        """
        return self.instance.stop()

    @check_installed
    async def update(self):
        """Update addon."""
        last_state = await self.state()

        if self.last_version == self.version_installed:
            _LOGGER.warning("No update available for Addon %s", self._id)
            return False

        if not await self.instance.update(self.last_version):
            return False
        self._set_update(self.last_version)

        # restore state
        if last_state == STATE_STARTED:
            await self.start()
        return True

    @check_installed
    async def restart(self):
        """Restart addon."""
        await self.stop()
        return await self.start()

    @check_installed
    def logs(self):
        """Return addons log output.

        Return a coroutine.
        """
        return self.instance.logs()

    @check_installed
    def stats(self):
        """Return stats of container.

        Return a coroutine.
        """
        return self.instance.stats()

    @check_installed
    async def rebuild(self):
        """Performe a rebuild of local build addon."""
        last_state = await self.state()

        if not self.need_build:
            _LOGGER.error("Can't rebuild a none local build addon!")
            return False

        # remove docker container but not addon config
        if not await self.instance.remove():
            return False

        if not await self.instance.install(self.version_installed):
            return False

        # restore state
        if last_state == STATE_STARTED:
            await self.start()
        return True

    @check_installed
    async def write_stdin(self, data):
        """Write data to add-on stdin.

        Return a coroutine.
        """
        if not self.with_stdin:
            _LOGGER.error("Add-on don't support write to stdin!")
            return False

        return await self.instance.write_stdin(data)

    @check_installed
    async def snapshot(self, tar_file):
        """Snapshot a state of a addon."""
        with TemporaryDirectory(dir=str(self._config.path_tmp)) as temp:
            # store local image
            if self.need_build and not await \
                    self.instance.export_image(Path(temp, "image.tar")):
                return False

            data = {
                ATTR_USER: self._data.user.get(self._id, {}),
                ATTR_SYSTEM: self._data.system.get(self._id, {}),
                ATTR_VERSION: self.version_installed,
                ATTR_STATE: await self.state(),
            }

            # store local configs/state
            try:
                write_json_file(Path(temp, "addon.json"), data)
            except (OSError, json.JSONDecodeError) as err:
                _LOGGER.error("Can't save meta for %s: %s", self._id, err)
                return False

            # write into tarfile
            def _write_tarfile():
                """Write tar inside loop."""
                with tar_file as snapshot:
                    snapshot.add(temp, arcname=".")
                    snapshot.add(self.path_data, arcname="data")

            try:
                _LOGGER.info("Build snapshot for addon %s", self._id)
                await self._loop.run_in_executor(None, _write_tarfile)
            except (tarfile.TarError, OSError) as err:
                _LOGGER.error("Can't write tarfile %s: %s", tar_file, err)
                return False

        _LOGGER.info("Finish snapshot for addon %s", self._id)
        return True

    async def restore(self, tar_file):
        """Restore a state of a addon."""
        with TemporaryDirectory(dir=str(self._config.path_tmp)) as temp:
            # extract snapshot
            def _extract_tarfile():
                """Extract tar snapshot."""
                with tar_file as snapshot:
                    snapshot.extractall(path=Path(temp))

            try:
                await self._loop.run_in_executor(None, _extract_tar)
            except tarfile.TarError as err:
                _LOGGER.error("Can't read tarfile %s: %s", tar_file, err)
                return False

            # read snapshot data
            try:
                data = read_json_file(Path(temp, "addon.json"))
            except (OSError, json.JSONDecodeError) as err:
                _LOGGER.error("Can't read addon.json: %s", err)

            # validate
            try:
                data = SCHEMA_ADDON_SNAPSHOT(data)
            except vol.Invalid as err:
                _LOGGER.error("Can't validate %s, snapshot data: %s",
                              self._id, humanize_error(data, err))
                return False

            # restore data / reload addon
            _LOGGER.info("Restore config for addon %s", self._id)
            self._restore_data(data[ATTR_USER], data[ATTR_SYSTEM])

            # check version / restore image
            version = data[ATTR_VERSION]
            if not await self.instance.exists():
                _LOGGER.info("Restore image for addon %s", self._id)

                image_file = Path(temp, "image.tar")
                if image_file.is_file():
                    await self.instance.import_image(image_file, version)
                else:
                    if await self.instance.install(version):
                        await self.instance.cleanup()
            else:
                await self.instance.stop()

            # restore data
            def _restore_data():
                """Restore data."""
                if self.path_data.is_dir():
                    shutil.rmtree(str(self.path_data), ignore_errors=True)
                shutil.copytree(str(Path(temp, "data")), str(self.path_data))

            try:
                _LOGGER.info("Restore data for addon %s", self._id)
                await self._loop.run_in_executor(None, _restore_data)
            except shutil.Error as err:
                _LOGGER.error("Can't restore origin data: %s", err)
                return False

            # run addon
            if data[ATTR_STATE] == STATE_STARTED:
                return await self.start()

        _LOGGER.info("Finish restore for addon %s", self._id)
        return True
