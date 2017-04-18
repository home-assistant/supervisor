"""Init file for HassIO docker object."""
import os

from . import DockerBase


class DockerSupervisor(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock, hassio, image=None):
        """Initialize docker base wrapper."""
        super().__init__(config, loop, dock, image=image)

        self.hassio = hassio

    @property
    def docker_name(self):
        """Return name of docker container."""
        return os.environ['SUPERVISOR_NAME']

    async def update(self, tag):
        """Update a supervisor docker image.

        Return a Future.
        """
        if self._lock.locked():
            _LOGGER.error("Can't excute update while a task is in progress")
            return False

        async with self._lock:
            if await self.loop.run_in_executor(None, self._update, tag):
                self.loop.create_task(self.hassio.stop(RESTART_EXIT_CODE))

    def _update(self, tag):
        """Update a docker image.

        Need run inside executor.
        """
        _LOGGER.info("Update supervisor docker to %s:%s", self.image, tag)

        # update docker image
        return self._install(tag)

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
