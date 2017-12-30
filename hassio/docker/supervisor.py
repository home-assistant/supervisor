"""Init file for HassIO docker object."""
import logging
import os

import docker

from .interface import DockerInterface
from .utils import docker_process

_LOGGER = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface):
    """Docker hassio wrapper for HomeAssistant."""

    @property
    def name(self):
        """Return name of docker container."""
        return os.environ['SUPERVISOR_NAME']

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        self._meta = container.attrs
        _LOGGER.info("Attach to supervisor %s with version %s",
                     self.image, self.version)

        # if already attach
        if container in self._docker.network.containers:
            return True

        # attach to network
        return self._docker.network.attach_container(
            container, alias=['hassio'], ipv4=self._docker.network.supervisor)

    @docker_process
    async def update(self, tag):
        """Update a supervisor docker image."""
        _LOGGER.info("Update supervisor docker to %s:%s", self.image, tag)

        if await self._loop.run_in_executor(None, self._install, tag):
            self._loop.call_later(1, self._loop.stop)
            return True

        return False

    async def run(self):
        """Run docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def install(self, tag):
        """Pull docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def stop(self):
        """Stop/remove docker container."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def remove(self):
        """Remove docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def restart(self):
        """Restart docker container."""
        raise RuntimeError("Not support on supervisor docker container!")
