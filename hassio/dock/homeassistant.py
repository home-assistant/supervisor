"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock):
        """Initialize docker homeassistant wrapper."""
        super().__init__(config, loop, dock, image=config.homeassistant_image)

    @property
    def name(self):
        """Return name of docker container."""
        return HASS_DOCKER_NAME

    @property
    def devices(self):
        """Create list of special device to map into docker."""
        if not self.config.homeassistant_devices:
            return

        devices = []
        for device in self.config.homeassistant_devices:
            devices.append("{0}:{0}:rwm".format(device))

        return devices

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
                privileged=True,
                devices=self.devices,
                network_mode='host',
                environment={
                    'HASSIO': self.config.api_endpoint,
                    'TZ': self.config.timezone,
                },
                volumes={
                    str(self.config.path_extern_config):
                        {'bind': '/config', 'mode': 'rw'},
                    str(self.config.path_extern_ssl):
                        {'bind': '/ssl', 'mode': 'ro'},
                    str(self.config.path_extern_share):
                        {'bind': '/share', 'mode': 'rw'},
                })

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        _LOGGER.info(
            "Start homeassistant %s with version %s", self.image, self.version)
        return True
