"""Init file for HassIO addon docker object."""
import logging

import docker

from . import DockerBase
from ..tools import get_version_from_env

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


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
            self.addons_data.path_extern_data(self.addon): {
                'bind': '/data', 'mode': 'rw'
            }}

        if self.addons_data.map_config(self.addon):
            volumes.update({
                self.config.path_extern_config: {
                    'bind': '/config', 'mode': 'rw'
                }})

        if self.addons_data.map_ssl(self.addon):
            volumes.update({
                self.config.path_extern_ssl: {
                    'bind': '/ssl', 'mode': 'rw'
                }})

        if self.addons_data.map_addons(self.addon):
            volumes.update({
                self.config.path_extern_addons_local: {
                    'bind': '/addons', 'mode': 'rw'
                }})

        if self.addons_data.map_backup(self.addon):
            volumes.update({
                self.config.path_extern_backup: {
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
            _LOGGER.info("Attach to image %s with version %s",
                         self.image, self.version)
        except (docker.errors.DockerException, KeyError):
            pass
