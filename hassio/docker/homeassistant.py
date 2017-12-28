"""Init file for HassIO docker object."""
import logging

import docker

from .interface import DockerInterface

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


class DockerHomeAssistant(DockerInterface):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, coresys):
        """Initialize docker homeassistant wrapper."""
        super().__init__(coresys)

    @property
    def image(self):
        """Return name of docker image."""
        return self._homeassistant.image

    @property
    def name(self):
        """Return name of docker container."""
        return HASS_DOCKER_NAME

    @property
    def devices(self):
        """Create list of special device to map into docker."""
        if not self._homeassistant.devices:
            return None

        devices = []
        for device in self._homeassistant.devices:
            devices.append("/dev/{0}:/dev/{0}:rwm".format(device))

        return devices

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return False

        # cleanup
        self._stop()

        ret = self._docker.run(
            self.image,
            name=self.name,
            hostname=self.name,
            detach=True,
            privileged=True,
            init=True,
            devices=self.devices,
            network_mode='host',
            environment={
                'HASSIO': self._docker.network.supervisor,
                'TZ': self._config.timezone,
            },
            volumes={
                str(self._config.path_extern_config):
                    {'bind': '/config', 'mode': 'rw'},
                str(self._config.path_extern_ssl):
                    {'bind': '/ssl', 'mode': 'ro'},
                str(self._config.path_extern_share):
                    {'bind': '/share', 'mode': 'rw'},
            }
        )

        if ret:
            _LOGGER.info("Start homeassistant %s with version %s",
                         self.image, self.version)

        return ret

    def _execute_command(self, command):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        return self._docker.run_command(
            self.image,
            command,
            detach=True,
            stdout=True,
            stderr=True,
            environment={
                'TZ': self._config.timezone,
            },
            volumes={
                str(self._config.path_extern_config):
                    {'bind': '/config', 'mode': 'ro'},
                str(self._config.path_extern_ssl):
                    {'bind': '/ssl', 'mode': 'ro'},
            }
        )

    def is_initialize(self):
        """Return True if docker container exists."""
        return self.loop.run_in_executor(None, self._is_initialize)

    def _is_initialize(self):
        """Return True if docker container exists.

        Need run inside executor.
        """
        try:
            self._docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        return True
