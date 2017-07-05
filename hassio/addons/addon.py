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
    validate_options, SCHEMA_ADDON_USER, SCHEMA_ADDON_SYSTEM,
    SCHEMA_ADDON_SNAPSHOT, MAP_VOLUME)
from ..const import (
    ATTR_NAME, ATTR_VERSION, ATTR_SLUG, ATTR_DESCRIPTON, ATTR_BOOT, ATTR_MAP,
    ATTR_OPTIONS, ATTR_PORTS, ATTR_SCHEMA, ATTR_IMAGE, ATTR_REPOSITORY,
    ATTR_URL, ATTR_ARCH, ATTR_LOCATON, ATTR_DEVICES, ATTR_ENVIRONMENT,
    ATTR_HOST_NETWORK, ATTR_TMPFS, ATTR_PRIVILEGED, ATTR_STARTUP,
    STATE_STARTED, STATE_STOPPED, STATE_NONE, ATTR_USER, ATTR_SYSTEM,
    ATTR_STATE)
from .util import check_installed
from ..dock.addon import DockerAddon
from ..tools import write_json_file, read_json_file

_LOGGER = logging.getLogger(__name__)

RE_VOLUME = re.compile(MAP_VOLUME)


class Addon(object):
    """Hold data for addon inside HassIO."""

    def __init__(self, config, loop, dock, data, slug):
        """Initialize data holder."""
        self.loop = loop
        self.config = config
        self.data = data
        self._id = slug

        self.addon_docker = DockerAddon(config, loop, dock, self)

    async def load(self):
        """Async initialize of object."""
        if self.is_installed:
            self._validate_system_user()
            await self.addon_docker.attach()

    def _validate_system_user(self):
        """Validate internal data they read from file."""
        for data, schema in ((self.data.system, SCHEMA_ADDON_SYSTEM),
                             (self.data.user, SCHEMA_ADDON_USER)):
            try:
                data[self._id] = schema(data[self._id])
            except vol.Invalid as err:
                _LOGGER.warning("Can't validate addon load %s -> %s", self._id,
                                humanize_error(data[self._id], err))
            except KeyError:
                pass

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
            return {
                **self.data.system[self._id][ATTR_OPTIONS],
                **self.data.user[self._id][ATTR_OPTIONS],
            }
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
    def name(self):
        """Return name of addon."""
        return self._mesh[ATTR_NAME]

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
        return self._mesh.get(ATTR_PORTS)

    @property
    def network_mode(self):
        """Return network mode of addon."""
        if self._mesh[ATTR_HOST_NETWORK]:
            return 'host'
        return 'bridge'

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
    def url(self):
        """Return url of addon."""
        return self._mesh.get(ATTR_URL)

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
    def path_addon_options(self):
        """Return path to addons options."""
        return Path(self.path_data, "options.json")

    @property
    def path_addon_location(self):
        """Return path to this addon."""
        return Path(self._mesh[ATTR_LOCATON])

    def write_options(self):
        """Return True if addon options is written to data."""
        schema = self.schema
        options = self.options

        try:
            schema(options)
            return write_json_file(self.path_addon_options, options)
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
        if not await self.addon_docker.install(version):
            return False

        self._set_install(version)
        return True

    @check_installed
    async def uninstall(self):
        """Remove a addon."""
        if not await self.addon_docker.remove():
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

        if await self.addon_docker.is_running():
            return STATE_STARTED
        return STATE_STOPPED

    @check_installed
    async def start(self):
        """Set options and start addon."""
        return await self.addon_docker.run()

    @check_installed
    async def stop(self):
        """Stop addon."""
        return await self.addon_docker.stop()

    @check_installed
    async def update(self, version=None):
        """Update addon."""
        version = version or self.last_version

        if version == self.version_installed:
            _LOGGER.warning(
                "Addon %s is already installed in %s", self._id, version)
            return True

        if not await self.addon_docker.update(version):
            return False

        self._set_update(version)
        return True

    @check_installed
    async def restart(self):
        """Restart addon."""
        return await self.addon_docker.restart()

    @check_installed
    async def logs(self):
        """Return addons log output."""
        return await self.addon_docker.logs()

    @check_installed
    async def snapshot(self, tar_file):
        """Snapshot a state of a addon."""
        with TemporaryDirectory(dir=str(self.config.path_tmp)) as temp:
            # store local image
            if self.need_build and not await \
                    self.addon_docker.export_image(Path(temp, "image.tar")):
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
                await self.loop.run_in_executor(None, _create_tar)
            except tarfile.TarError as err:
                _LOGGER.error("Can't write tarfile %s -> %s", tar_file, err)
                return False

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
            if version != self.addon_docker.version:
                image_file = Path(temp, "image.tar")
                if image_file.is_file():
                    await self.addon_docker.import_image(image_file, version)
                else:
                    if await self.addon_docker.install(version):
                        await self.addon_docker.cleanup()
            else:
                await self.addon_docker.stop()

            # restore data
            def _restore_data():
                """Restore data."""
                if self.path_data.is_dir():
                    shutil.rmtree(str(self.path_data), ignore_errors=True)
                shutil.copytree(str(Path(temp, "data")), str(self.path_data))

            try:
                await self.loop.run_in_executor(None, _restore_data)
            except shutil.Error as err:
                _LOGGER.error("Can't restore origin data -> %s", err)
                return False

            # run addon
            if data[ATTR_STATE] == STATE_STARTED:
                return await self.start()

        return True
