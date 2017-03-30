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

    async def install(self, tag='latest'):
        """Pull docker image."""
        raise RuntimeError("Not support on supervisor docker container!")
