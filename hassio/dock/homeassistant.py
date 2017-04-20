"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase
from ..tools import get_version_from_env

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock):
        """Initialize docker homeassistant wrapper."""
        super().__init__(config, loop, dock, image=config.homeassistant_image)

    @property
    def docker_name(self):
        """Return name of docker container."""
        return HASS_DOCKER_NAME

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
                privileged=True,
                network_mode='host',
                environment={
                    'HASSIO': self.config.api_endpoint,
                },
                volumes={
                    self.config.path_config_docker:
                        {'bind': '/config', 'mode': 'rw'},
                    self.config.path_ssl_docker:
                        {'bind': '/ssl', 'mode': 'rw'},
                })

            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])

            _LOGGER.info("Start docker addon %s with version %s",
                         self.image, self.version)

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        return True
