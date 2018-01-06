"""Interface class for HassIO docker object."""
import asyncio
from contextlib import suppress
import logging

import docker

from .utils import docker_process, calc_cpu_percent
from ..const import LABEL_VERSION, LABEL_ARCH
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class DockerInterface(CoreSysAttributes):
    """Docker hassio interface."""

    def __init__(self, coresys):
        """Initialize docker base wrapper."""
        self.coresys = coresys
        self._meta = None
        self.lock = asyncio.Lock(loop=self._loop)

    @property
    def timeout(self):
        """Return timeout for docker actions."""
        return 30

    @property
    def name(self):
        """Return name of docker container."""
        return None

    @property
    def image(self):
        """Return name of docker image."""
        if not self._meta:
            return None
        return self._meta['Config']['Image']

    @property
    def version(self):
        """Return version of docker image."""
        if self._meta and LABEL_VERSION in self._meta['Config']['Labels']:
            return self._meta['Config']['Labels'][LABEL_VERSION]
        return None

    @property
    def arch(self):
        """Return arch of docker image."""
        if self._meta and LABEL_ARCH in self._meta['Config']['Labels']:
            return self._meta['Config']['Labels'][LABEL_ARCH]
        return None

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.lock.locked()

    @docker_process
    def install(self, tag):
        """Pull docker image."""
        return self._loop.run_in_executor(None, self._install, tag)

    def _install(self, tag):
        """Pull docker image.

        Need run inside executor.
        """
        try:
            _LOGGER.info("Pull image %s tag %s.", self.image, tag)
            image = self._docker.images.pull(f"{self.image}:{tag}")

            image.tag(self.image, tag='latest')
            self._meta = image.attrs
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", self.image, tag, err)
            return False

        _LOGGER.info("Tag image %s with version %s as latest", self.image, tag)
        return True

    def exists(self):
        """Return True if docker image exists in local repo."""
        return self._loop.run_in_executor(None, self._exists)

    def _exists(self):
        """Return True if docker image exists in local repo.

        Need run inside executor.
        """
        try:
            image = self._docker.images.get(self.image)
            assert f"{self.image}:{self.version}" in image.tags
        except (docker.errors.DockerException, AssertionError):
            return False

        return True

    def is_running(self):
        """Return True if docker is Running.

        Return a Future.
        """
        return self._loop.run_in_executor(None, self._is_running)

    def _is_running(self):
        """Return True if docker is Running.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
            image = self._docker.images.get(self.image)
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
        return self._loop.run_in_executor(None, self._attach)

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            if self.image:
                self._meta = self._docker.images.get(self.image).attrs
            else:
                self._meta = self._docker.containers.get(self.name).attrs
        except docker.errors.DockerException:
            return False

        _LOGGER.info(
            "Attach to image %s with version %s", self.image, self.version)

        return True

    @docker_process
    def run(self):
        """Run docker image."""
        return self._loop.run_in_executor(None, self._run)

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        raise NotImplementedError()

    @docker_process
    def stop(self):
        """Stop/remove docker container."""
        return self._loop.run_in_executor(None, self._stop)

    def _stop(self):
        """Stop/remove and remove docker container.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
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
        return self._loop.run_in_executor(None, self._remove)

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
                self._docker.images.remove(
                    image=f"{self.image}:latest", force=True)

            with suppress(docker.errors.ImageNotFound):
                self._docker.images.remove(
                    image=f"{self.image}:{self.version}", force=True)

        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't remove image %s: %s", self.image, err)
            return False

        self._meta = None
        return True

    @docker_process
    def update(self, tag):
        """Update a docker image."""
        return self._loop.run_in_executor(None, self._update, tag)

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

    def logs(self):
        """Return docker logs of container.

        Return a Future.
        """
        return self._loop.run_in_executor(None, self._logs)

    def _logs(self):
        """Return docker logs of container.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
        except docker.errors.DockerException:
            return b""

        try:
            return container.logs(tail=100, stdout=True, stderr=True)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't grap logs from %s: %s", self.image, err)

    @docker_process
    def restart(self):
        """Restart docker container."""
        return self._loop.run_in_executor(None, self._restart)

    def _restart(self):
        """Restart docker container.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        _LOGGER.info("Restart %s", self.image)

        try:
            container.restart(timeout=self.timeout)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't restart %s: %s", self.image, err)
            return False

        return True

    @docker_process
    def cleanup(self):
        """Check if old version exists and cleanup."""
        return self._loop.run_in_executor(None, self._cleanup)

    def _cleanup(self):
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            latest = self._docker.images.get(self.image)
        except docker.errors.DockerException:
            _LOGGER.warning("Can't find %s for cleanup", self.image)
            return False

        for image in self._docker.images.list(name=self.image):
            if latest.id == image.id:
                continue

            with suppress(docker.errors.DockerException):
                _LOGGER.info("Cleanup docker images: %s", image.tags)
                self._docker.images.remove(image.id, force=True)

        return True

    @docker_process
    def execute_command(self, command):
        """Create a temporary container and run command."""
        return self._loop.run_in_executor(None, self._execute_command, command)

    def _execute_command(self, command):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        raise NotImplementedError()

    def stats(self):
        """Read and return stats from container."""
        return self._loop.run_in_executor(None, self._stats)

    def _stats(self):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
        except docker.errors.DockerException:
            return {}

        stats = container.stats(stream=False)
        return {
            ATTR_CPU_PERCENT: calc_cpu_percent(stats),
            ATTR_MEMORY_USAGE: stats['memory_stats']['usage'],
            ATTR_MEMORY_LIMIT: stats['memory_stats']['limit'],
        }
