"""Init file for HassIO docker object."""
import logging
import os

import docker

from .interface import DockerInterface
from .util import docker_process

_LOGGER = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, api, stop_callback, image=None):
        """Initialize docker base wrapper."""
        super().__init__(config, loop, api, image=image)
        self.stop_callback = stop_callback

    @property
    def name(self):
        """Return name of docker container."""
        return os.environ['SUPERVISOR_NAME']

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            container = self.docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        self.process_metadata(container.attrs)
        _LOGGER.info("Attach to supervisor %s with version %s",
                     self.image, self.version)

        # if already attach
        if container in self.docker.network.containers:
            return True

        # attach to network
        return self.docker.network.attach_container(
            container, alias=['hassio'], ipv4=self.docker.network.supervisor)

    @docker_process
    async def update(self, tag):
        """Update a supervisor docker image."""
        _LOGGER.info("Update supervisor docker to %s:%s", self.image, tag)

        if await self.loop.run_in_executor(None, self._install, tag):
            self.loop.call_later(2, self.loop.stop)
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
