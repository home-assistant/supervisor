"""Interface class for Hass.io Docker object."""
import asyncio
from contextlib import suppress
import logging
from typing import Any, Dict, Optional, Awaitable

import docker

from ..const import LABEL_ARCH, LABEL_VERSION
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DockerAPIError
from ..utils import process_lock
from .stats import DockerStats
from . import CommandReturn

_LOGGER = logging.getLogger(__name__)


class DockerInterface(CoreSysAttributes):
    """Docker Hass.io interface."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self._meta: Optional[Dict[str, Any]] = None
        self.lock: asyncio.Lock = asyncio.Lock(loop=coresys.loop)

    @property
    def timeout(self) -> str:
        """Return timeout for Docker actions."""
        return 30

    @property
    def name(self) -> Optional[str]:
        """Return name of Docker container."""
        return None

    @property
    def meta_config(self) -> Dict[str, Any]:
        """Return meta data of configuration for container/image."""
        if not self._meta:
            return {}
        return self._meta.get("Config", {})

    @property
    def meta_labels(self) -> Dict[str, str]:
        """Return meta data of labels for container/image."""
        return self.meta_config.get("Labels") or {}

    @property
    def image(self) -> Optional[str]:
        """Return name of Docker image."""
        return self.meta_config.get("Image")

    @property
    def version(self) -> Optional[str]:
        """Return version of Docker image."""
        return self.meta_labels.get(LABEL_VERSION)

    @property
    def arch(self) -> Optional[str]:
        """Return arch of Docker image."""
        return self.meta_labels.get(LABEL_ARCH)

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.lock.locked()

    @process_lock
    def install(self, tag: str, image: Optional[str] = None):
        """Pull docker image."""
        return self.sys_run_in_executor(self._install, tag, image)

    def _install(self, tag: str, image: Optional[str] = None) -> None:
        """Pull Docker image.

        Need run inside executor.
        """
        image = image or self.image
        image = image.partition(":")[0]  # remove potential tag

        try:
            _LOGGER.info("Pull image %s tag %s.", image, tag)
            docker_image = self.sys_docker.images.pull(f"{image}:{tag}")

            _LOGGER.info("Tag image %s with version %s as latest", image, tag)
            docker_image.tag(image, tag="latest")
        except docker.errors.APIError as err:
            _LOGGER.error("Can't install %s:%s -> %s.", image, tag, err)
            raise DockerAPIError() from None
        else:
            self._meta = docker_image.attrs

    def exists(self) -> Awaitable[bool]:
        """Return True if Docker image exists in local repository."""
        return self.sys_run_in_executor(self._exists)

    def _exists(self) -> bool:
        """Return True if Docker image exists in local repository.

        Need run inside executor.
        """
        try:
            docker_image = self.sys_docker.images.get(self.image)
            assert f"{self.image}:{self.version}" in docker_image.tags
        except (docker.errors.DockerException, AssertionError):
            return False

        return True

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker is running.

        Return a Future.
        """
        return self.sys_run_in_executor(self._is_running)

    def _is_running(self) -> bool:
        """Return True if Docker is running.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
            docker_image = self.sys_docker.images.get(self.image)
        except docker.errors.DockerException:
            return False

        # container is not running
        if docker_container.status != "running":
            return False

        # we run on an old image, stop and start it
        if docker_container.image.id != docker_image.id:
            return False

        return True

    @process_lock
    def attach(self):
        """Attach to running Docker container."""
        return self.sys_run_in_executor(self._attach)

    def _attach(self) -> None:
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            if self.image:
                self._meta = self.sys_docker.images.get(self.image).attrs
            self._meta = self.sys_docker.containers.get(self.name).attrs
        except docker.errors.DockerException:
            pass

        # Successfull?
        if not self._meta:
            raise DockerAPIError() from None
        _LOGGER.info("Attach to %s with version %s", self.image, self.version)

    @process_lock
    def run(self) -> Awaitable[None]:
        """Run Docker image."""
        return self.sys_run_in_executor(self._run)

    def _run(self) -> None:
        """Run Docker image.

        Need run inside executor.
        """
        raise NotImplementedError()

    @process_lock
    def stop(self, remove_container=True) -> Awaitable[None]:
        """Stop/remove Docker container."""
        return self.sys_run_in_executor(self._stop, remove_container)

    def _stop(self, remove_container=True) -> None:
        """Stop/remove Docker container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            raise DockerAPIError() from None

        if docker_container.status == "running":
            _LOGGER.info("Stop %s application", self.name)
            with suppress(docker.errors.DockerException):
                docker_container.stop(timeout=self.timeout)

        if remove_container:
            with suppress(docker.errors.DockerException):
                _LOGGER.info("Clean %s application", self.name)
                docker_container.remove(force=True)

    @process_lock
    def start(self) -> Awaitable[None]:
        """Start Docker container."""
        return self.sys_run_in_executor(self._start)

    def _start(self) -> None:
        """Start docker container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            raise DockerAPIError() from None

        _LOGGER.info("Start %s", self.image)
        try:
            docker_container.start()
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't start %s: %s", self.image, err)
            raise DockerAPIError() from None

    @process_lock
    def remove(self) -> Awaitable[None]:
        """Remove Docker images."""
        return self.sys_run_in_executor(self._remove)

    def _remove(self) -> None:
        """remove docker images.

        Need run inside executor.
        """
        # Cleanup container
        with suppress(DockerAPIError):
            self._stop()

        _LOGGER.info("Remove image %s with latest and %s", self.image, self.version)

        try:
            with suppress(docker.errors.ImageNotFound):
                self.sys_docker.images.remove(image=f"{self.image}:latest", force=True)

            with suppress(docker.errors.ImageNotFound):
                self.sys_docker.images.remove(
                    image=f"{self.image}:{self.version}", force=True
                )

        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't remove image %s: %s", self.image, err)
            raise DockerAPIError() from None

        self._meta = None

    @process_lock
    def update(self, tag: str, image: Optional[str] = None) -> Awaitable[None]:
        """Update a Docker image."""
        return self.sys_run_in_executor(self._update, tag, image)

    def _update(self, tag: str, image: Optional[str] = None) -> None:
        """Update a docker image.

        Need run inside executor.
        """
        image = image or self.image

        _LOGGER.info(
            "Update image %s:%s to %s:%s", self.image, self.version, image, tag
        )

        # Update docker image
        self._install(tag, image)

        # Stop container & cleanup
        with suppress(DockerAPIError):
            try:
                self._stop()
            finally:
                self._cleanup()

    def logs(self) -> Awaitable[bytes]:
        """Return Docker logs of container.

        Return a Future.
        """
        return self.sys_run_in_executor(self._logs)

    def _logs(self) -> bytes:
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
    def cleanup(self) -> Awaitable[None]:
        """Check if old version exists and cleanup."""
        return self.sys_run_in_executor(self._cleanup)

    def _cleanup(self) -> None:
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            latest = self.sys_docker.images.get(self.image)
        except docker.errors.DockerException:
            _LOGGER.warning("Can't find %s for cleanup", self.image)
            raise DockerAPIError() from None

        for image in self.sys_docker.images.list(name=self.image):
            if latest.id == image.id:
                continue

            with suppress(docker.errors.DockerException):
                _LOGGER.info("Cleanup images: %s", image.tags)
                self.sys_docker.images.remove(image.id, force=True)

    @process_lock
    def restart(self) -> Awaitable[None]:
        """Restart docker container."""
        return self.sys_loop.run_in_executor(None, self._restart)

    def _restart(self) -> None:
        """Restart docker container.

        Need run inside executor.
        """
        try:
            container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            raise DockerAPIError() from None

        _LOGGER.info("Restart %s", self.image)
        try:
            container.restart(timeout=self.timeout)
        except docker.errors.DockerException as err:
            _LOGGER.warning("Can't restart %s: %s", self.image, err)
            raise DockerAPIError() from None

    @process_lock
    def execute_command(self, command: str) -> Awaitable[CommandReturn]:
        """Create a temporary container and run command."""
        return self.sys_run_in_executor(self._execute_command, command)

    def _execute_command(self, command: str) -> CommandReturn:
        """Create a temporary container and run command.

        Need run inside executor.
        """
        raise NotImplementedError()

    def stats(self) -> Awaitable[DockerStats]:
        """Read and return stats from container."""
        return self.sys_run_in_executor(self._stats)

    def _stats(self) -> DockerStats:
        """Create a temporary container and run command.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            raise DockerAPIError() from None

        try:
            stats = docker_container.stats(stream=False)
            return DockerStats(stats)
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't read stats from %s: %s", self.name, err)
            raise DockerAPIError() from None

    def is_fails(self) -> Awaitable[bool]:
        """Return True if Docker is failing state.

        Return a Future.
        """
        return self.sys_run_in_executor(self._is_fails)

    def _is_fails(self) -> bool:
        """Return True if Docker is failing state.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        # container is not running
        if docker_container.status != "exited":
            return False

        # Check return value
        if int(docker_container.attrs["State"]["ExitCode"]) != 0:
            return True

        return False
