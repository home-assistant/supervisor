"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'hassio_cluster'


class DockerHassIOCluster(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock, arch):
        """Initialize docker homeassistant wrapper."""
        super().__init__(
            config, loop, dock, image="homeassistant/{}-hassio-cluster")

    @property
    def name(self):
        """Return name of docker container."""
        return HASS_DOCKER_NAME

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
                network_mode='bridge',
                environment={
                    'HASSIO': self.config.api_endpoint,
                    'TZ': self.config.timezone,
                },
                ports={
                    "9123/tcp": 9123,
                }
                volumes={
                    str(self.config.path_extern_hassio):
                        {'bind': '/data', 'mode': 'rw'},
                })

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        _LOGGER.info("Start %s with version %s", self.image, self.version)
        return True
