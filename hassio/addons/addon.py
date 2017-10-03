"""Init file for HassIO addons."""
from copy import deepcopy
import logging
import json
from pathlib import Path, PurePath
import re
import shutil
import tarfile
from tempfile import TemporaryDirectory

from deepmerge import Merger
import voluptuous as vol
from voluptuous.humanize import humanize_error

from .validate import (
    validate_options, SCHEMA_ADDON_SNAPSHOT, RE_VOLUME)
from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_BOOT, ATTR_MAP,
    ATTR_OPTIONS, ATTR_PORTS, ATTR_SCHEMA, ATTR_IMAGE, ATTR_REPOSITORY,
    ATTR_URL, ATTR_ARCH, ATTR_LOCATON, ATTR_DEVICES, ATTR_ENVIRONMENT,
    ATTR_HOST_NETWORK, ATTR_TMPFS, ATTR_PRIVILEGED, ATTR_STARTUP,
    STATE_STARTED, STATE_STOPPED, STATE_NONE, ATTR_USER, ATTR_SYSTEM,
    ATTR_STATE, ATTR_TIMEOUT, ATTR_AUTO_UPDATE, ATTR_NETWORK, ATTR_WEBUI,
    ATTR_HASSIO_API, ATTR_AUDIO, ATTR_AUDIO_OUTPUT, ATTR_AUDIO_INPUT,
    ATTR_GPIO, ATTR_HOMEASSISTANT_API)
from .util import check_installed
from ..dock.addon import DockerAddon
from ..tools import write_json_file, read_json_file

_LOGGER = logging.getLogger(__name__)

RE_WEBUI = re.compile(
    r"^(?:(?P<s_prefix>https?)|\[PROTO:(?P<t_proto>\w+)\])"
    r":\/\/\[HOST\]:\[PORT:(?P<t_port>\d+)\](?P<s_suffix>.*)$")

MERGE_OPT = Merger([(dict, ['merge'])], ['override'], ['override'])


class Addon(object):
    """Hold data for addon inside HassIO."""

    def __init__(self, config, loop, docker, data, slug):
        """Initialize data holder."""
        self.loop = loop
        self.config = config
        self.data = data
        self._id = slug

        self.docker = DockerAddon(config, loop, docker, self)

    async def load(self):
        """Async initialize of object."""
        if self.is_installed:
            await self.docker.attach()

    @property
    def slug(self):
        """Return slug/id of addon."""
        return self._id

    @property
    def _mesh(self):
        """Return addon data from system or cache."""
        return self.data.system.get(self._id, self.data.cache.get(self._id))

    @property
    def is_installed(self):
        """Return True if a addon is installed."""
        return self._id in self.data.system

    @property
    def is_detached(self):
        """Return True if addon is detached."""
        return self._id not in self.data.cache

    @property
    def version_installed(self):
        """Return installed version."""
        return self.data.user.get(self._id, {}).get(ATTR_VERSION)

    def _set_install(self, version):
        """Set addon as installed."""
        self.data.system[self._id] = deepcopy(self.data.cache[self._id])
        self.data.user[self._id] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: version,
        }
        self.data.save()

    def _set_uninstall(self):
        """Set addon as uninstalled."""
        self.data.system.pop(self._id, None)
        self.data.user.pop(self._id, None)
        self.data.save()

    def _set_update(self, version):
        """Update version of addon."""
        self.data.system[self._id] = deepcopy(self.data.cache[self._id])
        self.data.user[self._id][ATTR_VERSION] = version
        self.data.save()

    def _restore_data(self, user, system):
        """Restore data to addon."""
        self.data.user[self._id] = deepcopy(user)
        self.data.system[self._id] = deepcopy(system)
        self.data.save()

    @property
    def options(self):
        """Return options with local changes."""
        if self.is_installed:
            return MERGE_OPT.merge(
                self.data.system[self._id][ATTR_OPTIONS],
                self.data.user[self._id][ATTR_OPTIONS],
            )
        return self.data.cache[self._id][ATTR_OPTIONS]

    @options.setter
    def options(self, value):
        """Store user addon options."""
        self.data.user[self._id][ATTR_OPTIONS] = deepcopy(value)
        self.data.save()

    @property
    def boot(self):
        """Return boot config with prio local settings."""
        if ATTR_BOOT in self.data.user.get(self._id, {}):
            return self.data.user[self._id][ATTR_BOOT]
        return self._mesh[ATTR_BOOT]

    @boot.setter
    def boot(self, value):
        """Store user boot options."""
        self.data.user[self._id][ATTR_BOOT] = value
        self.data.save()

    @property
    def auto_update(self):
        """Return if auto update is enable."""
        if ATTR_AUTO_UPDATE in self.data.user.get(self._id, {}):
            return self.data.user[self._id][ATTR_AUTO_UPDATE]

    @auto_update.setter
    def auto_update(self, value):
        """Set auto update."""
        self.data.user[self._id][ATTR_AUTO_UPDATE] = value
        self.data.save()

    @property
    def name(self):
        """Return name of addon."""
        return self._mesh[ATTR_NAME]

    @property
    def timeout(self):
        """Return timeout of addon for docker stop."""
        return self._mesh[ATTR_TIMEOUT]

    @property
    def description(self):
        """Return description of addon."""
        return self._mesh[ATTR_DESCRIPTON]

    @property
    def repository(self):
        """Return repository of addon."""
        return self._mesh[ATTR_REPOSITORY]

    @property
    def last_version(self):
        """Return version of addon."""
        if self._id in self.data.cache:
            return self.data.cache[self._id][ATTR_VERSION]
        return self.version_installed

    @property
    def startup(self):
        """Return startup type of addon."""
        return self._mesh.get(ATTR_STARTUP)

    @property
    def ports(self):
        """Return ports of addon."""
        if self.host_network or ATTR_PORTS not in self._mesh:
            return None

        if not self.is_installed or \
                ATTR_NETWORK not in self.data.user[self._id]:
            return self._mesh[ATTR_PORTS]
        return self.data.user[self._id][ATTR_NETWORK]

    @ports.setter
    def ports(self, value):
        """Set custom ports of addon."""
        if value is None:
            self.data.user[self._id].pop(ATTR_NETWORK, None)
        else:
            new_ports = {}
            for container_port, host_port in value.items():
                if container_port in self._mesh.get(ATTR_PORTS, {}):
                    new_ports[container_port] = host_port

            self.data.user[self._id][ATTR_NETWORK] = new_ports

        self.data.save()

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
            port = self.ports.get("{}/tcp".format(t_port), t_port)
        else:
            port = t_port

        # for interface config or port lists
        if isinstance(port, (tuple, list)):
            port = port[-1]

        # lookup the correct protocol from config
        if t_proto:
            proto = 'https' if self.options[t_proto] else 'http'
        else:
            proto = s_prefix

        return "{}://[HOST]:{}{}".format(proto, port, s_suffix)

    @property
    def host_network(self):
        """Return True if addon run on host network."""
        return self._mesh[ATTR_HOST_NETWORK]

    @property
    def devices(self):
        """Return devices of addon."""
        return self._mesh.get(ATTR_DEVICES)

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
    def access_hassio_api(self):
        """Return True if the add-on access to hassio api."""
        return self._mesh[ATTR_HASSIO_API]

    @property
    def access_homeassistant_api(self):
        """Return True if the add-on access to Home-Assistant api proxy."""
        return self._mesh[ATTR_HOMEASSISTANT_API]

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

        setting = self.config.audio_output
        if self.is_installed and ATTR_AUDIO_OUTPUT in self.data.user[self._id]:
            setting = self.data.user[self._id][ATTR_AUDIO_OUTPUT]
        return setting

    @audio_output.setter
    def audio_output(self, value):
        """Set/remove custom audio output settings."""
        if value is None:
            self.data.user[self._id].pop(ATTR_AUDIO_OUTPUT, None)
        else:
            self.data.user[self._id][ATTR_AUDIO_OUTPUT] = value
        self.data.save()

    @property
    def audio_input(self):
        """Return ALSA config for input or None."""
        if not self.with_audio:
            return

        setting = self.config.audio_input
        if self.is_installed and ATTR_AUDIO_INPUT in self.data.user[self._id]:
            setting = self.data.user[self._id][ATTR_AUDIO_INPUT]
        return setting

    @audio_input.setter
    def audio_input(self, value):
        """Set/remove custom audio input settings."""
        if value is None:
            self.data.user[self._id].pop(ATTR_AUDIO_INPUT, None)
        else:
            self.data.user[self._id][ATTR_AUDIO_INPUT] = value
        self.data.save()

    @property
    def url(self):
        """Return url of addon."""
        return self._mesh.get(ATTR_URL)

    @property
    def with_logo(self):
        """Return True if a logo exists."""
        return self.path_logo.exists()

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
            return addon_data[ATTR_IMAGE].format(arch=self.config.arch)

        # local build
        return "{}/{}-addon-{}".format(
            addon_data[ATTR_REPOSITORY], self.config.arch,
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
        return Path(self.config.path_addons_data, self._id)

    @property
    def path_extern_data(self):
        """Return addon data path external for docker."""
        return PurePath(self.config.path_extern_addons_data, self._id)

    @property
    def path_options(self):
        """Return path to addons options."""
        return Path(self.path_data, "options.json")

    @property
    def path_location(self):
        """Return path to this addon."""
        return Path(self._mesh[ATTR_LOCATON])

    @property
    def path_logo(self):
        """Return path to addon logo."""
        return Path(self.path_location, 'logo.png')

    def write_options(self):
        """Return True if addon options is written to data."""
        schema = self.schema
        options = self.options

        try:
            schema(options)
            return write_json_file(self.path_options, options)
        except vol.Invalid as ex:
            _LOGGER.error("Addon %s have wrong options -> %s", self._id,
                          humanize_error(options, ex))

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
        new_raw_schema = self.data.cache[self._id][ATTR_SCHEMA]
        default_options = self.data.cache[self._id][ATTR_OPTIONS]

        # if disabled
        if isinstance(new_raw_schema, bool):
            return True

        # merge options
        options = {
            **self.data.user[self._id][ATTR_OPTIONS],
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

    async def install(self, version=None):
        """Install a addon."""
        if self.config.arch not in self.supported_arch:
            _LOGGER.error(
                "Addon %s not supported on %s", self._id, self.config.arch)
            return False

        if self.is_installed:
            _LOGGER.error("Addon %s is already installed", self._id)
            return False

        if not self.path_data.is_dir():
            _LOGGER.info(
                "Create Home-Assistant addon data folder %s", self.path_data)
            self.path_data.mkdir()

        version = version or self.last_version
        if not await self.docker.install(version):
            return False

        self._set_install(version)
        return True

    @check_installed
    async def uninstall(self):
        """Remove a addon."""
        if not await self.docker.remove():
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

        if await self.docker.is_running():
            return STATE_STARTED
        return STATE_STOPPED

    @check_installed
    def start(self):
        """Set options and start addon.

        Return a coroutine.
        """
        return self.docker.run()

    @check_installed
    def stop(self):
        """Stop addon.

        Return a coroutine.
        """
        return self.docker.stop()

    @check_installed
    async def update(self, version=None):
        """Update addon."""
        version = version or self.last_version
        last_state = await self.state()

        if version == self.version_installed:
            _LOGGER.warning(
                "Addon %s is already installed in %s", self._id, version)
            return False

        if not await self.docker.update(version):
            return False
        self._set_update(version)

        # restore state
        if last_state == STATE_STARTED:
            await self.docker.run()
        return True

    @check_installed
    def restart(self):
        """Restart addon.

        Return a coroutine.
        """
        return self.docker.restart()

    @check_installed
    def logs(self):
        """Return addons log output.

        Return a coroutine.
        """
        return self.docker.logs()

    @check_installed
    async def rebuild(self):
        """Performe a rebuild of local build addon."""
        last_state = await self.state()

        if not self.need_build:
            _LOGGER.error("Can't rebuild a none local build addon!")
            return False

        # remove docker container but not addon config
        if not await self.docker.remove():
            return False

        if not await self.docker.install(self.version_installed):
            return False

        # restore state
        if last_state == STATE_STARTED:
            await self.docker.run()
        return True

    @check_installed
    async def snapshot(self, tar_file):
        """Snapshot a state of a addon."""
        with TemporaryDirectory(dir=str(self.config.path_tmp)) as temp:
            # store local image
            if self.need_build and not await \
                    self.docker.export_image(Path(temp, "image.tar")):
                return False

            data = {
                ATTR_USER: self.data.user.get(self._id, {}),
                ATTR_SYSTEM: self.data.system.get(self._id, {}),
                ATTR_VERSION: self.version_installed,
                ATTR_STATE: await self.state(),
            }

            # store local configs/state
            if not write_json_file(Path(temp, "addon.json"), data):
                _LOGGER.error("Can't write addon.json for %s", self._id)
                return False

            # write into tarfile
            def _create_tar():
                """Write tar inside loop."""
                with tarfile.open(tar_file, "w:gz",
                                  compresslevel=1) as snapshot:
                    snapshot.add(temp, arcname=".")
                    snapshot.add(self.path_data, arcname="data")

            try:
                _LOGGER.info("Build snapshot for addon %s", self._id)
                await self.loop.run_in_executor(None, _create_tar)
            except tarfile.TarError as err:
                _LOGGER.error("Can't write tarfile %s -> %s", tar_file, err)
                return False

        _LOGGER.info("Finish snapshot for addon %s", self._id)
        return True

    async def restore(self, tar_file):
        """Restore a state of a addon."""
        with TemporaryDirectory(dir=str(self.config.path_tmp)) as temp:
            # extract snapshot
            def _extract_tar():
                """Extract tar snapshot."""
                with tarfile.open(tar_file, "r:gz") as snapshot:
                    snapshot.extractall(path=Path(temp))

            try:
                await self.loop.run_in_executor(None, _extract_tar)
            except tarfile.TarError as err:
                _LOGGER.error("Can't read tarfile %s -> %s", tar_file, err)
                return False

            # read snapshot data
            try:
                data = read_json_file(Path(temp, "addon.json"))
            except (OSError, json.JSONDecodeError) as err:
                _LOGGER.error("Can't read addon.json -> %s", err)

            # validate
            try:
                data = SCHEMA_ADDON_SNAPSHOT(data)
            except vol.Invalid as err:
                _LOGGER.error("Can't validate %s, snapshot data -> %s",
                              self._id, humanize_error(data, err))
                return False

            # restore data / reload addon
            self._restore_data(data[ATTR_USER], data[ATTR_SYSTEM])

            # check version / restore image
            version = data[ATTR_VERSION]
            if version != self.docker.version:
                image_file = Path(temp, "image.tar")
                if image_file.is_file():
                    await self.docker.import_image(image_file, version)
                else:
                    if await self.docker.install(version):
                        await self.docker.cleanup()
            else:
                await self.docker.stop()

            # restore data
            def _restore_data():
                """Restore data."""
                if self.path_data.is_dir():
                    shutil.rmtree(str(self.path_data), ignore_errors=True)
                shutil.copytree(str(Path(temp, "data")), str(self.path_data))

            try:
                _LOGGER.info("Restore data for addon %s", self._id)
                await self.loop.run_in_executor(None, _restore_data)
            except shutil.Error as err:
                _LOGGER.error("Can't restore origin data -> %s", err)
                return False

            # run addon
            if data[ATTR_STATE] == STATE_STARTED:
                return await self.start()

        _LOGGER.info("Finish restore for addon %s", self._id)
        return True
