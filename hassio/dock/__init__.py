"""Init file for HassIO docker object."""
import asyncio
from contextlib import suppress
import logging

import docker

from .util import docker_process
from ..const import LABEL_VERSION, LABEL_ARCH

_LOGGER = logging.getLogger(__name__)


class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, config, loop, dock, image=None, timeout=30):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.dock = dock
        self.image = image
        self.timeout = timeout
        self.version = None
        self.arch = None
        self._lock = asyncio.Lock(loop=loop)

    @property
    def name(self):
        """Return name of docker container."""
        return None

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self._lock.locked()

    def process_metadata(self, metadata, force=False):
        """Read metadata and set it to object."""
        # read image
        if not self.image:
            self.image = metadata['Config']['Image']

        # read version
        need_version = force or not self.version
        if need_version and LABEL_VERSION in metadata['Config']['Labels']:
            self.version = metadata['Config']['Labels'][LABEL_VERSION]
        elif need_version:
            _LOGGER.warning("Can't read version from %s", self.name)

        # read arch
        need_arch = force or not self.arch
        if need_arch and LABEL_ARCH in metadata['Config']['Labels']:
            self.arch = metadata['Config']['Labels'][LABEL_ARCH]

    @docker_process
    def install(self, tag):
        """Pull docker image."""
        return self.loop.run_in_executor(None, self._install, tag)

    def _install(self, tag):
        """Pull docker image.

        Need run inside executor.
        """
        try:
            _LOGGER.info("Pull image %s tag %s.", self.image, tag)
            image = self.dock.images.pull("{}:{}".format(self.image, tag))

            image.tag(self.image, tag='latest')
            self.process_metadata(image.attrs, force=True)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", self.image, tag, err)
            return False

        _LOGGER.info("Tag image %s with version %s as latest", self.image, tag)
        return True

    def exists(self):
        """Return True if docker image exists in local repo."""
        return self.loop.run_in_executor(None, self._exists)

    def _exists(self):
        """Return True if docker image exists in local repo.

        Need run inside executor.
        """
        try:
            self.dock.images.get(self.image)
        except docker.errors.DockerException:
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
        try:
            container = self.dock.containers.get(self.name)
            image = self.dock.images.get(self.image)
        except docker.errors.DockerException:
            return False

        # container is not running
        if container.status != 'running':
            return False

        # we run on a old image, stop and start it
        if container.image.id != image.id:
            return False

        return True

    @docker_process
    def attach(self):
        """Attach to running docker container."""
        return self.loop.run_in_executor(None, self._attach)

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            if self.image:
                obj_data = self.dock.images.get(self.image).attrs
            else:
                obj_data = self.dock.containers.get(self.name).attrs
        except docker.errors.DockerException:
            return False

        self.process_metadata(obj_data)
        _LOGGER.info(
            "Attach to image %s with version %s", self.image, self.version)

        return True

    @docker_process
    def run(self):
        """Run docker image."""
        return self.loop.run_in_executor(None, self._run)

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        raise NotImplementedError()

    @docker_process
    def stop(self):
        """Stop/remove docker container."""
        return self.loop.run_in_executor(None, self._stop)

    def _stop(self):
        """Stop/remove and remove docker container.

        Need run inside executor.
        """
        try:
            container = self.dock.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        if container.status == 'running':
            _LOGGER.info("Stop %s docker application", self.image)
            with suppress(docker.errors.DockerException):
                container.stop(timeout=self.timeout)

        with suppress(docker.errors.DockerException):
            _LOGGER.info("Clean %s docker application", self.image)
            container.remove(force=True)

        return True

    @docker_process
    def remove(self):
        """Remove docker images."""
        return self.loop.run_in_executor(None, self._remove)

    def _remove(self):
        """remove docker images.

        Need run inside executor.
        """
        # cleanup container
        self._stop()

        _LOGGER.info(
            "Remove docker %s with latest and %s", self.image, self.version)

        try:
            with suppress(docker.errors.ImageNotFound):
                self.dock.images.remove(
                    image="{}:latest".format(self.image), force=True)

            with suppress(docker.errors.ImageNotFound):
                self.dock.images.remove(
                    image="{}:{}".format(self.image, self.version), force=True)

        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't remove image %s -> %s", self.image, err)
            return False

        # clean metadata
        self.version = None
        self.arch = None

        return True

    @docker_process
    def update(self, tag):
        """Update a docker image."""
        return self.loop.run_in_executor(None, self._update, tag)

    def _update(self, tag):
        """Update a docker image.

        Need run inside executor.
        """
        _LOGGER.info(
            "Update docker %s with %s:%s", self.version, self.image, tag)

        # update docker image
        if not self._install(tag):
            return False

        # stop container & cleanup
        self._stop()
        self._cleanup()

        return True

    @docker_process
    def logs(self):
        """Return docker logs of container."""
        return self.loop.run_in_executor(None, self._logs)

    def _logs(self):
        """Return docker logs of container.

        Need run inside executor.
        """
        try:
            container = self.dock.containers.get(self.name)
        except docker.errors.DockerException:
            return b""

        try:
            return container.logs(tail=100, stdout=True, stderr=True)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't grap logs from %s -> %s", self.image, err)

    @docker_process
    def restart(self):
        """Restart docker container."""
        return self.loop.run_in_executor(None, self._restart)

    def _restart(self):
        """Restart docker container.

        Need run inside executor.
        """
        try:
            container = self.dock.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        _LOGGER.info("Restart %s", self.image)

        try:
            container.restart(timeout=self.timeout)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't restart %s -> %s", self.image, err)
            return False

        return True

    @docker_process
    def cleanup(self):
        """Check if old version exists and cleanup."""
        return self.loop.run_in_executor(None, self._cleanup)

    def _cleanup(self):
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            latest = self.dock.images.get(self.image)
        except docker.errors.DockerException:
            _LOGGER.warning("Can't find %s for cleanup", self.image)
            return False

        for image in self.dock.images.list(name=self.image):
            if latest.id == image.id:
                continue

            with suppress(docker.errors.DockerException):
                _LOGGER.info("Cleanup docker images: %s", image.tags)
                self.dock.images.remove(image.id, force=True)

        return True

    @docker_process
    def execute_command(self, command):
        """Create a temporary container and run command."""
        return self.loop.run_in_executor(None, self._execute_command, command)

    def _execute_command(self, command):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        raise NotImplementedError()
