"""Init file for HassIO docker object."""
import logging

import docker

from .network import DockerNetwork
from ..const import SOCKET_DOCKER

_LOGGER = logging.getLogger(__name__)


class DockerAPI(object):
    """Docker hassio wrapper."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.docker = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)), version='auto')
        self.network = DockerNetwork(self.docker)

    @property
    def images(self):
        """Return api images."""
        return self.docker.images

    @property
    def containers(self):
        """Return api containers."""
        return self.docker.containers

    @property
    def api(self):
        """Return api containers."""
        return self.docker.api

    def run(self):
        """"Create a docker and run it.

        Need run inside executor.
        """

    def run_command(self, image, command=None, **kwargs):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        stdout = kwargs.get('stdout', True)
        stderr = kwargs.get('stderr', True)

        _LOGGER.info("Run command '%s' on %s", command, image)
        try:
            container = self.docker.containers.run(
                image,
                command=command,
                network=self.network.name,
                **kwargs
            )

            # wait until command is done
            exit_code = container.wait()
            output = container.logs(stdout=stdout, stderr=stderr)

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't execute command -> %s", err)
            return (None, b"")

        # cleanup container
        with suppress(docker.errors.DockerException):
            container.remove(force=True)

        return (exit_code, output)
