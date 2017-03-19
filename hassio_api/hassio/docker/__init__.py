"""Init file for HassIO docker object."""
import asyncio

import docker


class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, loop, dock, image, tag=None):
        """Initialize docker base wrapper."""
        self.loop = loop
        self.dock = dock
        self.image = image
        self.tag = tag

    async def install(tag='latest'):
        """Pull docker image."""
        try:
            self.dock.images.pull(self.image, tag=tag)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't pull %s:%s", self.image, tag)
            return False
        return True

    async def run():
        """Run docker image."""
        raise NotImplementedError()
