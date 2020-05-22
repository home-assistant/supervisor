"""Interface class for Supervisor Docker object."""
import asyncio
from contextlib import suppress
import logging
from typing import Any, Awaitable, Dict, List, Optional

import docker

from . import CommandReturn
from ..const import LABEL_ARCH, LABEL_VERSION
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DockerAPIError
from ..utils import process_lock
from .stats import DockerStats

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DockerInterface(CoreSysAttributes):
    """Docker Supervisor interface."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self._meta: Optional[Dict[str, Any]] = None
        self.lock: asyncio.Lock = asyncio.Lock()

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
    def meta_host(self) -> Dict[str, Any]:
        """Return meta data of configuration for host."""
        if not self._meta:
            return {}
        return self._meta.get("HostConfig", {})

    @property
    def meta_labels(self) -> Dict[str, str]:
        """Return meta data of labels for container/image."""
        return self.meta_config.get("Labels") or {}

    @property
    def image(self) -> Optional[str]:
        """Return name of Docker image."""
        try:
            return self.meta_config["Image"].partition(":")[0]
        except KeyError:
            return None

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
    def install(self, tag: str, image: Optional[str] = None, latest: bool = False):
        """Pull docker image."""
        return self.sys_run_in_executor(self._install, tag, image, latest)

    def _install(
        self, tag: str, image: Optional[str] = None, latest: bool = False
    ) -> None:
        """Pull Docker image.

        Need run inside executor.
        """
        image = image or self.image

        _LOGGER.info("Pull image %s tag %s.", image, tag)
        try:
            docker_image = self.sys_docker.images.pull(f"{image}:{tag}")
            if latest:
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
        with suppress(docker.errors.DockerException):
            self.sys_docker.images.get(f"{self.image}:{self.version}")
            return True
        return False

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
        except docker.errors.DockerException:
            return False

        # container is not running
        if docker_container.status != "running":
            return False

        return True

    @process_lock
    def attach(self, tag: str):
        """Attach to running Docker container."""
        return self.sys_run_in_executor(self._attach, tag)

    def _attach(self, tag: str) -> None:
        """Attach to running docker container.

        Need run inside executor.
        """
        with suppress(docker.errors.DockerException):
            self._meta = self.sys_docker.containers.get(self.name).attrs

        with suppress(docker.errors.DockerException):
            if not self._meta and self.image:
                self._meta = self.sys_docker.images.get(f"{self.image}:{tag}").attrs

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
        """Remove docker images.

        Needs run inside executor.
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
    def update(
        self, tag: str, image: Optional[str] = None, latest: bool = False
    ) -> Awaitable[None]:
        """Update a Docker image."""
        return self.sys_run_in_executor(self._update, tag, image, latest)

    def _update(
        self, tag: str, image: Optional[str] = None, latest: bool = False
    ) -> None:
        """Update a docker image.

        Need run inside executor.
        """
        image = image or self.image

        _LOGGER.info(
            "Update image %s:%s to %s:%s", self.image, self.version, image, tag
        )

        # Update docker image
        self._install(tag, image=image, latest=latest)

        # Stop container & cleanup
        with suppress(DockerAPIError):
            self._stop()

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
    def cleanup(self, old_image: Optional[str] = None) -> Awaitable[None]:
        """Check if old version exists and cleanup."""
        return self.sys_run_in_executor(self._cleanup, old_image)

    def _cleanup(self, old_image: Optional[str] = None) -> None:
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            origin = self.sys_docker.images.get(f"{self.image}:{self.version}")
        except docker.errors.DockerException:
            _LOGGER.warning("Can't find %s for cleanup", self.image)
            raise DockerAPIError() from None

        # Cleanup Current
        for image in self.sys_docker.images.list(name=self.image):
            if origin.id == image.id:
                continue

            with suppress(docker.errors.DockerException):
                _LOGGER.info("Cleanup images: %s", image.tags)
                self.sys_docker.images.remove(image.id, force=True)

        # Cleanup Old
        if not old_image or self.image == old_image:
            return

        for image in self.sys_docker.images.list(name=old_image):
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

    def get_latest_version(self, key: Any = int) -> Awaitable[str]:
        """Return latest version of local Home Asssistant image."""
        return self.sys_run_in_executor(self._get_latest_version, key)

    def _get_latest_version(self, key: Any = int) -> str:
        """Return latest version of local Home Asssistant image.

        Need run inside executor.
        """
        available_version: List[str] = []
        try:
            for image in self.sys_docker.images.list(self.image):
                for tag in image.tags:
                    version = tag.partition(":")[2]
                    try:
                        key(version)
                    except (AttributeError, ValueError):
                        continue
                    available_version.append(version)

            if not available_version:
                raise ValueError()

        except (docker.errors.DockerException, ValueError):
            _LOGGER.debug("No version found for %s", self.image)
            raise DockerAPIError()
        else:
            _LOGGER.debug("Found %s versions: %s", self.image, available_version)

        # Sort version and return latest version
        available_version.sort(key=key, reverse=True)
        return available_version[0]
