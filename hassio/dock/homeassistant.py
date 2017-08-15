"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock, data):
        """Initialize docker homeassistant wrapper."""
        super().__init__(config, loop, dock, image=data.image)
        self.data = data

    @property
    def name(self):
        """Return name of docker container."""
        return HASS_DOCKER_NAME

    @property
    def devices(self):
        """Create list of special device to map into docker."""
        if not self.data.devices:
            return

        devices = []
        for device in self.data.devices:
            devices.append("/dev/{0}:/dev/{0}:rwm".format(device))

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
                hostname=self.name,
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
                }
            )

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        _LOGGER.info(
            "Start homeassistant %s with version %s", self.image, self.version)
        return True

    def _execute_command(self, command):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        _LOGGER.info("Run command '%s' on %s", command, self.image)
        try:
            output = self.dock.containers.run(
                self.image,
                command=command,
                remove=True,
                detach=False,
                stdout=True,
                stderr=True,
                environment={
                    'TZ': self.config.timezone,
                },
                volumes={
                    str(self.config.path_extern_config):
                        {'bind': '/config', 'mode': 'ro'},
                    str(self.config.path_extern_ssl):
                        {'bind': '/ssl', 'mode': 'ro'},
                }
            )

        except docker.errors.ContainerError as err:
            return str(err).encode()

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't execute command -> %s", command, err)
            return b""

        return output
