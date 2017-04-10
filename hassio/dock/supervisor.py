"""Init file for HassIO docker object."""
import os

from . import DockerBase


class DockerSupervisor(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    @property
    def docker_name(self):
        """Return name of docker container."""
        return os.environ['SUPERVISOR_NAME']

    async def run(self):
        """Run docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def install(self, tag):
        """Pull docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def stop(self):
        """Stop/remove docker container."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def update(self, tag):
        """Update docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def remove(self, tag):
        """Remove docker image."""
        raise RuntimeError("Not support on supervisor docker container!")
