"""Interface class for Hass.io Docker object."""
import asyncio
from contextlib import suppress
import logging

import docker

from .stats import DockerStats
from ..const import LABEL_VERSION, LABEL_ARCH
from ..coresys import CoreSysAttributes
from ..utils import process_lock

_LOGGER = logging.getLogger(__name__)


class DockerInterface(CoreSysAttributes):
    """Docker Hass.io interface."""

    def __init__(self, coresys):
        """Initialize Docker base wrapper."""
        self.coresys = coresys
        self._meta = None
        self.lock = asyncio.Lock(loop=coresys.loop)

    @property
    def timeout(self):
        """Return timeout for Docker actions."""
        return 30

    @property
    def name(self):
        """Return name of Docker container."""
        return None

    @property
    def meta_config(self):
        """Return meta data of configuration for container/image."""
        if not self._meta:
            return {}
        return self._meta.get('Config', {})

    @property
    def meta_labels(self):
        """Return meta data of labels for container/image."""
        return self.meta_config.get('Labels') or {}

    @property
    def image(self):
        """Return name of Docker image."""
        return self.meta_config.get('Image')

    @property
    def version(self):
        """Return version of Docker image."""
        return self.meta_labels.get(LABEL_VERSION)

    @property
    def arch(self):
        """Return arch of Docker image."""
        return self.meta_labels.get(LABEL_ARCH)

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self.lock.locked()

    @process_lock
    def install(self, tag, image=None):
        """Pull docker image."""
        return self.sys_run_in_executor(self._install, tag, image)

    def _install(self, tag, image=None):
        """Pull Docker image.

        Need run inside executor.
        """
        image = image or self.image

        try:
            _LOGGER.info("Pull image %s tag %s.", image, tag)
            docker_image = self.sys_docker.images.pull(f"{image}:{tag}")

            docker_image.tag(image, tag='latest')
            self._meta = docker_image.attrs
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", image, tag, err)
            return False

        _LOGGER.info("Tag image %s with version %s as latest", image, tag)
        return True

    def exists(self):
        """Return True if Docker image exists in local repository."""
        return self.sys_run_in_executor(self._exists)

    def _exists(self):
        """Return True if Docker image exists in local repository.

        Need run inside executor.
        """
        try:
            docker_image = self.sys_docker.images.get(self.image)
            assert f"{self.image}:{self.version}" in docker_image.tags
        except (docker.errors.DockerException, AssertionError):
            return False

        return True

    def is_running(self):
        """Return True if Docker is running.

        Return a Future.
        """
        return self.sys_run_in_executor(self._is_running)

    def _is_running(self):
        """Return True if Docker is running.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
            docker_image = self.sys_docker.images.get(self.image)
        except docker.errors.DockerException:
            return False

        # container is not running
        if docker_container.status != 'running':
            return False

        # we run on an old image, stop and start it
        if docker_container.image.id != docker_image.id:
            return False

        return True

    @process_lock
    def attach(self):
        """Attach to running Docker container."""
        return self.sys_run_in_executor(self._attach)

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            if self.image:
                self._meta = self.sys_docker.images.get(self.image).attrs
            else:
                self._meta = self.sys_docker.containers.get(self.name).attrs
        except docker.errors.DockerException:
            return False

        _LOGGER.info("Attach to image %s with version %s", self.image,
                     self.version)

        return True

    @process_lock
    def run(self):
        """Run Docker image."""
        return self.sys_run_in_executor(self._run)

    def _run(self):
        """Run Docker image.

        Need run inside executor.
        """
        raise NotImplementedError()

    @process_lock
    def stop(self):
        """Stop/remove Docker container."""
        return self.sys_run_in_executor(self._stop)

    def _stop(self):
        """Stop/remove and remove docker container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        if docker_container.status == 'running':
            _LOGGER.info("Stop %s Docker application", self.image)
            with suppress(docker.errors.DockerException):
                docker_container.stop(timeout=self.timeout)

        with suppress(docker.errors.DockerException):
            _LOGGER.info("Clean %s Docker application", self.image)
            docker_container.remove(force=True)

        return True

    @process_lock
    def remove(self):
        """Remove Docker images."""
        return self.sys_run_in_executor(self._remove)

    def _remove(self):
        """remove docker images.

        Need run inside executor.
        """
        # Cleanup container
        self._stop()

        _LOGGER.info("Remove Docker %s with latest and %s", self.image,
                     self.version)

        try:
            with suppress(docker.errors.ImageNotFound):
                self.sys_docker.images.remove(
                    image=f"{self.image}:latest", force=True)

            with suppress(docker.errors.ImageNotFound):
                self.sys_docker.images.remove(
                    image=f"{self.image}:{self.version}", force=True)

        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't remove image %s: %s", self.image, err)
            return False

        self._meta = None
        return True

    @process_lock
    def update(self, tag, image=None):
        """Update a Docker image."""
        return self.sys_run_in_executor(self._update, tag, image)

    def _update(self, tag, image=None):
        """Update a docker image.

        Need run inside executor.
        """
        image = image or self.image

        _LOGGER.info("Update Docker %s:%s to %s:%s", self.image, self.version,
                     image, tag)

        # Update docker image
        if not self._install(tag, image):
            return False

        # Stop container & cleanup
        self._stop()
        self._cleanup()

        return True

    def logs(self):
        """Return Docker logs of container.

        Return a Future.
        """
        return self.sys_run_in_executor(self._logs)

    def _logs(self):
        """Return Docker logs of container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            return b""

        try:
            return docker_container.logs(tail=100, stdout=True, stderr=True)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't grep logs from %s: %s", self.image, err)

    @process_lock
    def cleanup(self):
        """Check if old version exists and cleanup."""
        return self.sys_run_in_executor(self._cleanup)

    def _cleanup(self):
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            latest = self.sys_docker.images.get(self.image)
        except docker.errors.DockerException:
            _LOGGER.warning("Can't find %s for cleanup", self.image)
            return False

        for image in self.sys_docker.images.list(name=self.image):
            if latest.id == image.id:
                continue

            with suppress(docker.errors.DockerException):
                _LOGGER.info("Cleanup Docker images: %s", image.tags)
                self.sys_docker.images.remove(image.id, force=True)

        return True

    @process_lock
    def execute_command(self, command):
        """Create a temporary container and run command."""
        return self.sys_run_in_executor(self._execute_command, command)

    def _execute_command(self, command):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        raise NotImplementedError()

    def stats(self):
        """Read and return stats from container."""
        return self.sys_run_in_executor(self._stats)

    def _stats(self):
        """Create a temporary container and run command.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            return None

        try:
            stats = docker_container.stats(stream=False)
            return DockerStats(stats)
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't read stats from %s: %s", self.name, err)
            return None
