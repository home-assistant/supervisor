"""Init file for HassIO docker object."""
import asyncio
from contextlib import suppress
import logging

import docker

from ..const import LABEL_VERSION

_LOGGER = logging.getLogger(__name__)


class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, config, loop, dock, image=None):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.dock = dock
        self.image = image
        self.version = None
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

        # read metadata
        need_version = force or not self.version
        if need_version and LABEL_VERSION in metadata['Config']['Labels']:
            self.version = metadata['Config']['Labels'][LABEL_VERSION]
        elif need_version:
            _LOGGER.warning("Can't read version from %s", self.name)

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
            self.process_metadata(image.attrs, force=True)
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", self.image, tag, err)
            return False

        _LOGGER.info("Tag image %s with version %s as latest", self.image, tag)
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
            _ = self.dock.images.get(self.image)
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
        if container.id != image.id:
            return False

        return True

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

    async def run(self):
        """Run docker image."""
        if self._lock.locked():
            _LOGGER.error("Can't excute run while a task is in progress")
            return False

        async with self._lock:
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
        try:
            container = self.dock.containers.get(self.name)
        except docker.errors.DockerException:
            return

        _LOGGER.info("Stop %s docker application", self.image)

        if container.status == 'running':
            with suppress(docker.errors.DockerException):
                container.stop()

        with suppress(docker.errors.DockerException):
            container.remove(force=True)

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

        return True

    async def update(self, tag):
        """Update a docker image."""
        if self._lock.locked():
            _LOGGER.error("Can't excute update while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._update, tag)

    def _update(self, tag):
        """Update a docker image.

        Need run inside executor.
        """
        old_image = "{}:{}".format(self.image, self.version)

        _LOGGER.info("Update docker %s with %s:%s",
                     old_image, self.image, tag)

        # update docker image
        if self._install(tag):
            _LOGGER.info("Cleanup old %s docker", old_image)
            self._stop()
            try:
                self.dock.images.remove(image=old_image, force=True)
            except docker.errors.DockerException as err:
                _LOGGER.warning(
                    "Can't remove old image %s -> %s", old_image, err)
            return True

        return False

    async def logs(self):
        """Return docker logs of container."""
        if self._lock.locked():
            _LOGGER.error("Can't excute logs while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._logs)

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

    async def restart(self):
        """Restart docker container."""
        if self._lock.locked():
            _LOGGER.error("Can't excute restart while a task is in progress")
            return False

        async with self._lock:
            return await self.loop.run_in_executor(None, self._restart)

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
            container.restart(timeout=30)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't restart %s -> %s", self.image, err)
            return False

        return True
