"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase
from ..tools import get_version_from_env, get_local_ip

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

        api_endpoint = get_local_ip(self.loop)

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
                environment={
                    'HASSIO': api_endpoint,
                },
                volumes={
                    self.config.path_config_docker:
                        {'bind': '/config', 'mode': 'rw'},
                    self.config.path_ssl_docker:
                        {'bind': '/ssl', 'mode': 'rw'},
                })

            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])
        except docker.errors.DockerException:
            _LOGGER.error("Can't run %s", self.image)
            return False

        return True
