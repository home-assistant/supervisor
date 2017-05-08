"""Init file for HassIO docker object."""
import logging
import os

import docker

from . import DockerBase
from ..const import RESTART_EXIT_CODE

_LOGGER = logging.getLogger(__name__)


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
        """Update a supervisor docker image."""
        if self._lock.locked():
            _LOGGER.error("Can't excute update while a task is in progress")
            return False

        _LOGGER.info("Update supervisor docker to %s:%s", self.image, tag)
        old_version = self.version

        async with self._lock:
            if await self.loop.run_in_executor(None, self._install, tag):
                self.config.hassio_cleanup = old_version
                self.loop.create_task(self.hassio.stop(RESTART_EXIT_CODE))
                return True

            return False

    async def cleanup(self):
        """Check if old supervisor version exists and cleanup."""
        if not self.config.hassio_cleanup:
            return

        async with self._lock:
            if await self.loop.run_in_executor(None, self._cleanup):
                self.config.hassio_cleanup = None

    def _cleanup(self):
        """Remove old image.

        Need run inside executor.
        """
        old_image = "{}:{}".format(self.image, self.config.hassio_cleanup)

        _LOGGER.info("Old supervisor docker found %s", old_image)
        try:
            self.dock.images.remove(image=old_image, force=True)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't remove old image %s -> %s", old_image, err)
            return False

        return True

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
