"""Init file for HassIO docker object."""
import asyncio

import docker

import . from DockerBase


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    async def run():
        """Run docker image."""
        try:
            self.docker.images.pull(self.image, tag=tag)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't pull %s:%s", self.image, tag)
            return False

        return True
