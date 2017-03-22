"""Init file for HassIO docker object."""
import logging

import docker

_LOGGER = logging.getLogger(__name__)


class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, config, loop, dock, image, tag=None):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.dock = dock
        self.image = image
        self.tag = tag
        self.container = None

    @property
    def docker_name(self):
        """Return name of docker container."""
        return None

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

    def is_running(self):
        """Return True if docker is Running.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._is_running)

    def _is_running(self):
        """Return True if docker is Running.

        Need run inside executor.
        """
        if not self.container:
            try:
                self.container = self.dock.containers.get(self.docker_name)
            except docker.errors.DockerException:
                return False
        return self.container.status == 'running'

    def run(self):
        """Run docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._run, tag)

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        raise NotImplementedError()
