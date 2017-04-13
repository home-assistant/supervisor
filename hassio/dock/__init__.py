"""Init file for HassIO docker object."""
import asyncio
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
        self._lock = asyncio.Lock(loop=loop)

    @property
    def docker_name(self):
        """Return name of docker container."""
        return None

    @property
    def in_progress(self):
        """Return True if a task is in progress."""
        return self._lock.locked()

    async def install(self, tag):
        """Pull docker image."""
        if self._lock.locked():
            _LOGGER.error("Can't excute install while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._install, tag)

    def _install(self, tag):
        """Pull docker image.

        Need run inside executor.
        """
        try:
            _LOGGER.info("Pull image %s tag %s.", self.image, tag)
            image = self.dock.images.pull("{}:{}".format(self.image, tag))

            image.tag(self.image, tag='latest')
            self.version = get_version_from_env(image.attrs['Config']['Env'])
            _LOGGER.info("Tag image %s with version %s as latest",
                         self.image, self.version)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", self.image, tag, err)
            return False
        return True

    def exists(self):
        """Return True if docker image exists in local repo.

        Return a Future.
        """
        return self.loop.run_in_executor(None, self._exists)

    def _exists(self):
        """Return True if docker image exists in local repo.

        Need run inside executor.
        """
        try:
            image = self.dock.images.get(self.image)
            self.version = get_version_from_env(image.attrs['Config']['Env'])
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
        if not self.container:
            try:
                self.container = self.dock.containers.get(self.docker_name)
                self.version = get_version_from_env(
                    self.container.attrs['Config']['Env'])
            except docker.errors.DockerException:
                return False

        self.container.reload()
        return self.container.status == 'running'

    async def attach(self):
        """Attach to running docker container."""
        if self._lock.locked():
            _LOGGER.error("Can't excute attach while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._attach)

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            self.container = self.dock.containers.get(self.docker_name)
            self.image = self.container.attrs['Config']['Image']
            self.version = get_version_from_env(
                self.container.attrs['Config']['Env'])
            _LOGGER.info("Attach to image %s with version %s",
                         self.image, self.version)
        except (docker.errors.DockerException, KeyError):
            _LOGGER.fatal(
                "Can't attach to %s docker container!", self.docker_name)
            return False

        return True

    async def run(self):
        """Run docker image."""
        if self._lock.locked():
            _LOGGER.error("Can't excute run while a task is in progress")
            return False

        async with self._lock:
            _LOGGER.info("Run docker image %s with version %s",
                         self.image, self.version)
            return await self.loop.run_in_executor(None, self._run)

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        raise NotImplementedError()

    async def stop(self):
        """Stop/remove docker container."""
        if self._lock.locked():
            _LOGGER.error("Can't excute stop while a task is in progress")
            return False

        async with self._lock:
            await self.loop.run_in_executor(None, self._stop)
            return True

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

    async def remove(self):
        """Remove docker container."""
        if self._lock.locked():
            _LOGGER.error("Can't excute remove while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._remove)

    def _remove(self):
        """remove docker container.

        Need run inside executor.
        """
        if self._is_running():
            self._stop()

        image = "{}:latest".format(self.image)
        try:
            self.dock.images.remove(image=image, force=True)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't remove image %s -> %s", image, err)
            return False

        return True

    async def update(self, tag):
        """Update a docker image.

        Return a Future.
        """
        if self._lock.locked():
            _LOGGER.error("Can't excute update while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._update, tag)

    def _update(self, tag):
        """Update a docker image.

        Need run inside executor.
        """
        old_run = self._is_running()
        old_image = "{}:{}".format(self.image, self.version)

        _LOGGER.info("Update docker %s with %s:%s",
                     old_image, self.image, tag)

        # update docker image
        if self._install(tag):
            _LOGGER.info("Cleanup old %s docker.", old_image)
            self._stop()
            try:
                self.dock.images.remove(image=old_image, force=True)
            except docker.errors.DockerException as err:
                _LOGGER.warning(
                    "Can't remove old image %s -> %s", old_image, err)
            # restore
            if old_run:
                self._run()
            return True

        return False
