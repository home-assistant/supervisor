"""Init file for HassIO addon docker object."""
import logging

import docker

from . import DockerBase
from ..tools import get_version_from_env

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


class DockerAddon(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock, addon_config, addon):
        """Initialize docker homeassistant wrapper."""
        super().__init__(
            config, loop, dock, image=addon_config.get_image(addon))
        self.addon = addon
        self.addon_config

    @property
    def docker_name(self):
        """Return name of docker container."""
        return "addon_{}".format(self.addon_config.get_slug(self.addon))

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # cleanup old container
        self._stop()

        # volumes
        volumes = {
            self.addon_config.path_data_docker(self.addon): {
                'bind': '/data', 'mode': 'rw'
            }}
        if self.addon_config.need_config(self.addon):
            volumes.update({
                self.config.path_config_docker: {
                    'bind': '/config', 'mode': 'rw'
                }})
        if self.addon_config.need_ssl(self.addon):
            volumes.update({
                self.config.path_ssl_docker: {
                    'bind': '/ssl', 'mode': 'rw'
                }})

        try:
            self.container = self.dock.containers.run(
                self.image,
                name=self.docker_name,
                detach=True,
                network_mode='bridge',
                ports=self.addon_config.get_ports(self.addon),
                restart_policy={
                    "Name": "on-failure",
                    "MaximumRetryCount": 10,
                },
                volumes=volumes,
            )

            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s.", self.image, err)
            return False

        return True
