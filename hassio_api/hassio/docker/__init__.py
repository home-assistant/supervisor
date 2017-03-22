"""Init file for HassIO docker object."""
import asyncio

import docker

_LOGGER = logging.getLogger(__name__)

class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, loop, dock, image, tag=None):
        """Initialize docker base wrapper."""
        self.loop = loop
        self.dock = dock
        self.image = image
        self.tag = tag
        self.container = None

    def install(self, tag='latest'):
        """Pull docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._install, tag)

    def _install(self, tag='latest'):
        """Pull docker image.

        Need run inside executor.
        """
        try:
            self.dock.images.pull(self.image, tag=tag)

            if tag != "latest":
                image = self.dock.images.get("{}:{}".format(self.image, tag))
                image.tag(self.image, tag='latest')
        except docker.errors.APIError as err:
            _LOGGER.error("Can't pull %s:%s", self.image, tag)
            return False
        return True

    def run():
        """Run docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._run, tag)

    def _run():
        """Run docker image.

        Need run inside executor.
        """
        raise NotImplementedError()
