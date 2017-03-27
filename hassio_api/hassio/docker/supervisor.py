"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase
from ..const import HASSIO_DOCKER
from ..tools import get_version_from_env, extract_image_name

_LOGGER = logging.getLogger(__name__)


class DockerSupervisor(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock):
        """Initialize docker base wrapper."""
        super().__init__(config, loop, dock, None):

    def attach(self):
        """Pull docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._attach)

    def _attach(self):
        """Attach object to supervisor container.

        Need run inside executor.
        """
        try:
            self.container = dock.containers.get(self.docker_name)
            self.image, self.tag = self.image = extract_image_name(
                self.container.attrs['Config']['Image'])
            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])
        except (docker.errors.DockerException, KeyError):
            _LOGGER.fatal("Can't attach to supervisor docker container!")

    @property
    def docker_name(self):
        """Return name of docker container."""
        return HASSIO_DOCKER

    async def run(self):
        """Run docker image."""
        raise RuntimeError("Not support on supervisor docker container!")

    async def install(self, tag='latest'):
        """Pull docker image."""
        raise RuntimeError("Not support on supervisor docker container!")
