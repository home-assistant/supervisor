"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase
from ..const import HASSIO_DOCKER

_LOGGER = logging.getLogger(__name__)
HASS_DOCKER_NAME = 'homeassistant'


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock):
        """Initialize docker homeassistant wrapper."""
        super().__init__(
            config, loop, dock, image=config.homeassistant_image,
            tag=config.homeassistant_tag
        )

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

        try:
            self.container = self.dock.containers.run(
                self.image,
                name=self.docker_name,
                remove=True,
                privileged=True,
                network_mode='host',
                restart_policy={
                    "Name": "always",
                    "MaximumRetryCount": 10,
                },
                links={HASSIO_DOCKER: 'HASSIO'},
                volumes={
                    self.config.path_config_docker:
                        {'bind': '/config', 'mode': 'rw'},
                    self.config.path_ssl_docker:
                        {'bind': '/ssl', 'mode': 'rw'},
                })
        except docker.errors.DockerException:
            _LOGGER.error("Can't run %s", self.image)
            return False

        return True
