"""Init file for HassIO addon docker object."""
from distutils.dir_util import copy_tree
import logging
from pathlib import Path, PurePath
from tempfile import TemporaryDirectory

import docker

from . import DockerBase
from .util import dockerfile_template
from ..tools import get_version_from_env

_LOGGER = logging.getLogger(__name__)


class DockerAddon(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock, addons_data, addon):
        """Initialize docker homeassistant wrapper."""
        super().__init__(
            config, loop, dock, image=addons_data.get_image(addon))
        self.addon = addon
        self.addons_data = addons_data

    @property
    def docker_name(self):
        """Return name of docker container."""
        return "addon_{}".format(self.addon)

    @property
    def volumes(self):
        """Generate volumes for mappings."""
        volumes = {
            str(self.addons_data.path_extern_data(self.addon)): {
                'bind': '/data', 'mode': 'rw'
            }}

        if self.addons_data.map_config(self.addon):
            volumes.update({
                str(self.config.path_extern_config): {
                    'bind': '/config', 'mode': 'rw'
                }})

        if self.addons_data.map_ssl(self.addon):
            volumes.update({
                str(self.config.path_extern_ssl): {
                    'bind': '/ssl', 'mode': 'rw'
                }})

        if self.addons_data.map_addons(self.addon):
            volumes.update({
                str(self.config.path_extern_addons_local): {
                    'bind': '/addons', 'mode': 'rw'
                }})

        if self.addons_data.map_backup(self.addon):
            volumes.update({
                str(self.config.path_extern_backup): {
                    'bind': '/backup', 'mode': 'rw'
                }})

        return volumes

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # cleanup old container
        self._stop()

        try:
            self.container = self.dock.containers.run(
                self.image,
                name=self.docker_name,
                detach=True,
                network_mode='bridge',
                ports=self.addons_data.get_ports(self.addon),
                volumes=self.volumes,
            )

            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])

            _LOGGER.info("Start docker addon %s with version %s",
                         self.image, self.version)

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        return True

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            self.container = self.dock.containers.get(self.docker_name)
            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])

            _LOGGER.info(
                "Attach to image %s with version %s", self.image, self.version)
        except (docker.errors.DockerException, KeyError):
            pass

    def _install(self, tag):
        """Pull docker image or build it.

        Need run inside executor.
        """
        if self.addons_data.need_build(self.addon):
            return self._build(tag)

        return super()._install(tag)

    async def build(self, tag):
        """Build a docker container."""
        if self._lock.locked():
            _LOGGER.error("Can't excute build while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._build, tag)

    def _build(self, tag):
        """Build a docker container.

        Need run inside executor.
        """
        addon_build_path = str(self.config.path_addons_build)
        with TemporaryDirectory(dir=str(addon_build_path)) as tmp_dir:

            # prepare temporary addon build folder
            try:
                source = self.addons_data.path_addon_location(self.addon)
                copy_tree(str(source), tmp_dir)
            except shutil.Error as err:
                _LOGGER.error("Can't copy %s to temporary build folder -> %s",
                              source, tmp_dir)
                return False

            # prepare Dockerfile
            try:
                dockerfile_template(
                    Path(tmp_dir, 'Dockerfile'), self.addons_data.arch, tag)
            except OSError as err:
                _LOGGER.error("Can't prepare dockerfile -> %s", err)

            # run docker build
            try:
                build_tag = "{}:{}".format(self.image, tag)
                build_path = PurePath(
                    self.config.path_extern_addons_build,
                    PurePath(tmp_dir).parts[-1])

                _LOGGER.info("Start build %s on %s", build_tag, build_path)
                self.dock.images.build(path=str(build_path), tag=build_tag)
            except (docker.errors.DockerException, TypeError) as err:
                _LOGGER.error("Can't build %s -> %s", build_tag, err)
                return False

            _LOGGER.info("Build %s done", build_tag)
            return True
