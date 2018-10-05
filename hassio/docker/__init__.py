"""Init file for Hass.io Docker object."""
from contextlib import suppress
import logging

import attr
import docker

from .network import DockerNetwork
from ..const import SOCKET_DOCKER

_LOGGER = logging.getLogger(__name__)


@attr.s(frozen=True)
class CommandReturn:
    exit_code = attr.ib()
    output = attr.ib()


class DockerAPI:
    """Docker Hass.io wrapper.

    This class is not AsyncIO safe!
    """

    def __init__(self):
        """Initialize Docker base wrapper."""
        self.docker = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)),
            version='auto', timeout=900)
        self.network = DockerNetwork(self.docker)

    @property
    def images(self):
        """Return API images."""
        return self.docker.images

    @property
    def containers(self):
        """Return API containers."""
        return self.docker.containers

    @property
    def api(self):
        """Return API containers."""
        return self.docker.api

    def run(self, image, **kwargs):
        """"Create a Docker container and run it.

        Need run inside executor.
        """
        name = kwargs.get('name', image)
        network_mode = kwargs.get('network_mode')
        hostname = kwargs.get('hostname')

        # Setup network
        kwargs['dns_search'] = ["."]
        if network_mode:
            kwargs['dns'] = [str(self.network.supervisor)]
            kwargs['dns_opt'] = ["ndots:0"]
        else:
            kwargs['network'] = None

        # Create container
        try:
            container = self.docker.containers.create(image, **kwargs)
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't create container from %s: %s", name, err)
            return False

        # attach network
        if not network_mode:
            alias = [hostname] if hostname else None
            if self.network.attach_container(container, alias=alias):
                self.network.detach_default_bridge(container)
            else:
                _LOGGER.warning("Can't attach %s to hassio-net!", name)

        # run container
        try:
            container.start()
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't start %s: %s", name, err)
            return False

        return True

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
            result = container.wait()
            output = container.logs(stdout=stdout, stderr=stderr)

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't execute command: %s", err)
            return CommandReturn(None, b"")

        finally:
            # cleanup container
            with suppress(docker.errors.DockerException):
                container.remove(force=True)

        return CommandReturn(result.get('StatusCode'), output)
