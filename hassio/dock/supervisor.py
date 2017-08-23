"""Init file for HassIO docker object."""
import logging
import os

from .interface import DockerInterface
from .util import docker_process
from ..const import RESTART_EXIT_CODE

_LOGGER = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, docker, stop_callback, image=None):
        """Initialize docker base wrapper."""
        super().__init__(config, loop, docker, image=image)
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
            container = self.docker.containers.get(self.name).attrs
        except docker.errors.DockerException:
            return False
        else:
            self.process_metadata(container)

        _LOGGER.info("Attach to supervisor %s with version %s",
                     self.image, self.version)

        # attach to network
        return self.docker.network.attach_container(
            container, alias=['hassio'], ipv4=self.docker.network.supervisor)

    @docker_process
    async def update(self, tag):
        """Update a supervisor docker image."""
        _LOGGER.info("Update supervisor docker to %s:%s", self.image, tag)

        if await self.loop.run_in_executor(None, self._install, tag):
            self.loop.create_task(self.stop_callback(RESTART_EXIT_CODE))
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
