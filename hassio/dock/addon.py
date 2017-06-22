"""Init file for HassIO addon docker object."""
from contextlib import suppress
import logging
from pathlib import Path
import shutil

import docker

from . import DockerBase
from .util import dockerfile_template
from ..const import (
    META_ADDON, MAP_CONFIG, MAP_SSL, MAP_ADDONS, MAP_BACKUP, MAP_SHARE)

_LOGGER = logging.getLogger(__name__)


class DockerAddon(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock, addon):
        """Initialize docker homeassistant wrapper."""
        super().__init__(
            config, loop, dock, image=addon.image)
        self.addon = addon

    @property
    def name(self):
        """Return name of docker container."""
        return "addon_{}".format(self.addon.slug)

    @property
    def environment(self):
        """Return environment for docker add-on."""
        addon_env = self.addon.environment or {}

        return {
            **addon_env,
            'TZ': self.config.timezone,
        }

    @property
    def tmpfs(self):
        """Return tmpfs for docker add-on."""
        options = self.addon.tmpfs
        if options:
            return {"/tmpfs": "{}".format(options)}
        return None

    @property
    def volumes(self):
        """Generate volumes for mappings."""
        volumes = {
            str(self.addon.path_extern_data): {
                'bind': '/data', 'mode': 'rw'
            }}

        addon_mapping = self.addon.map_volumes

        if MAP_CONFIG in addon_mapping:
            volumes.update({
                str(self.config.path_extern_config): {
                    'bind': '/config', 'mode': addon_mapping[MAP_CONFIG]
                }})

        if MAP_SSL in addon_mapping:
            volumes.update({
                str(self.config.path_extern_ssl): {
                    'bind': '/ssl', 'mode': addon_mapping[MAP_SSL]
                }})

        if MAP_ADDONS in addon_mapping:
            volumes.update({
                str(self.config.path_extern_addons_local): {
                    'bind': '/addons', 'mode': addon_mapping[MAP_ADDONS]
                }})

        if MAP_BACKUP in addon_mapping:
            volumes.update({
                str(self.config.path_extern_backup): {
                    'bind': '/backup', 'mode': addon_mapping[MAP_BACKUP]
                }})

        if MAP_SHARE in addon_mapping:
            volumes.update({
                str(self.config.path_extern_share): {
                    'bind': '/share', 'mode': addon_mapping[MAP_SHARE]
                }})

        return volumes

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # cleanup
        self._stop()

        try:
            self.dock.containers.run(
                self.image,
                name=self.name,
                detach=True,
                network_mode=self.addon.network_mode,
                ports=self.addon.ports,
                devices=self.addon.devices,
                cap_add=self.addon.privileged,
                environment=self.environment,
                volumes=self.volumes,
                tmpfs=self.tmpfs
            )

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        _LOGGER.info(
            "Start docker addon %s with version %s", self.image, self.version)
        return True

    def _install(self, tag):
        """Pull docker image or build it.

        Need run inside executor.
        """
        if self.addon.need_build:
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
        build_dir = Path(self.config.path_addons_build, self.addon.slug)
        try:
            # prepare temporary addon build folder
            try:
                source = self.addon.path_addon_location
                shutil.copytree(str(source), str(build_dir))
            except shutil.Error as err:
                _LOGGER.error("Can't copy %s to temporary build folder -> %s",
                              source, build_dir)
                return False

            # prepare Dockerfile
            try:
                dockerfile_template(
                    Path(build_dir, 'Dockerfile'), self.config.arch,
                    tag, META_ADDON)
            except OSError as err:
                _LOGGER.error("Can't prepare dockerfile -> %s", err)

            # run docker build
            try:
                build_tag = "{}:{}".format(self.image, tag)

                _LOGGER.info("Start build %s on %s", build_tag, build_dir)
                image = self.dock.images.build(
                    path=str(build_dir), tag=build_tag, pull=True)

                image.tag(self.image, tag='latest')
                self.process_metadata(image.attrs, force=True)

            except (docker.errors.DockerException, TypeError) as err:
                _LOGGER.error("Can't build %s -> %s", build_tag, err)
                return False

            _LOGGER.info("Build %s done", build_tag)
            return True

        finally:
            shutil.rmtree(str(build_dir), ignore_errors=True)

    def _restart(self):
        """Restart docker container.

        Addons prepare some thing on start and that is normaly not repeatable.
        Need run inside executor.
        """
        try:
            container = self.dock.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        _LOGGER.info("Restart %s", self.image)

        with suppress(docker.errors.DockerException):
            container.stop(timeout=15)

        return self._run()
