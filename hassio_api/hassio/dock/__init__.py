"""Init file for HassIO docker object."""
from contextlib import suppress
import logging

import docker

from ..tools import get_version_from_env

_LOGGER = logging.getLogger(__name__)


class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, config, loop, dock, image=None):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.dock = dock
        self.image = image
        self.container = None
        self.version = None

    @property
    def docker_name(self):
        """Return name of docker container."""
        return None

    def install(self, tag):
        """Pull docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._install, tag)

    def _install(self, tag):
        """Pull docker image.

        Need run inside executor.
        """
        try:
            _LOGGER.info("Pull image %s tag %s.", self.image, tag)
            image = self.dock.images.pull("{}:{}".format(self.image, tag))

            image.tag(self.image, tag='latest')
            self.version = get_version_from_env(image.attrs['Config']['Env'])
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", self.image, tag, err)
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
                self.version = get_version_from_env(
                    self.container.attrs['Config']['Env'])
            except docker.errors.DockerException:
                return False

        self.container.reload()
        return self.container.status == 'running'

    def attach(self):
        """Attach to running docker container.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._attach)

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            self.container = self.dock.containers.get(self.docker_name)
            self.image = self.container.attrs['Config']['Image']
            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])
        except (docker.errors.DockerException, KeyError):
            _LOGGER.fatal(
                "Can't attach to %s docker container!", self.docker_name)

    def run(self):
        """Run docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._run)

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        raise NotImplementedError()

    def stop(self):
        """Stop/remove docker container.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._stop)

    def _stop(self):
        """Stop/remove and remove docker container.

        Need run inside executor.
        """
        if not self.container:
            return

        self.container.reload()
        if self.container.status == 'running':
            with suppress(docker.errors.DockerException):
                self.container.stop()

        with suppress(docker.errors.DockerException):
            self.container.remove(force=True)

        self.container = None

    def update(self, tag):
        """Update a docker image.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._update, tag)

    def _update(self, tag):
        """Update a docker image.

        Need run inside executor.
        """
        if self.container:
            self._stop()

        old_image = "{}:{}".format(self.image, self.version)
        if self._install(tag):
            try:
                self.dock.images.remove(image=old_image, force=True)
                return True
            except docker.errors.DockerException as err:
                _LOGGER.warning(
                    "Can't remove old image %s -> %s.", old_image, err)
                return False
