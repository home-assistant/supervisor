"""Interface class for Supervisor Docker object."""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import logging
import re
from time import time
from typing import Any

from awesomeversion import AwesomeVersion
from awesomeversion.strategy import AwesomeVersionStrategy
import docker
from docker.models.containers import Container
import requests

from ..const import (
    ATTR_PASSWORD,
    ATTR_REGISTRY,
    ATTR_USERNAME,
    LABEL_ARCH,
    LABEL_VERSION,
    BusEvent,
    CpuArch,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    CodeNotaryError,
    CodeNotaryUntrusted,
    DockerAPIError,
    DockerError,
    DockerNotFound,
    DockerRequestError,
    DockerTrustError,
)
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils import process_lock
from ..utils.sentry import capture_exception
from .const import ContainerState, RestartPolicy
from .manager import CommandReturn
from .monitor import DockerContainerStateEvent
from .stats import DockerStats

_LOGGER: logging.Logger = logging.getLogger(__name__)

IMAGE_WITH_HOST = re.compile(r"^((?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,})\/.+")
DOCKER_HUB = "hub.docker.com"

MAP_ARCH = {
    CpuArch.ARMV7: "linux/arm/v7",
    CpuArch.ARMHF: "linux/arm/v6",
    CpuArch.AARCH64: "linux/arm64",
    CpuArch.I386: "linux/386",
    CpuArch.AMD64: "linux/amd64",
}


def _container_state_from_model(docker_container: Container) -> ContainerState:
    """Get container state from model."""
    if docker_container.status == "running":
        if "Health" in docker_container.attrs["State"]:
            return (
                ContainerState.HEALTHY
                if docker_container.attrs["State"]["Health"]["Status"] == "healthy"
                else ContainerState.UNHEALTHY
            )
        return ContainerState.RUNNING

    if docker_container.attrs["State"]["ExitCode"] > 0:
        return ContainerState.FAILED

    return ContainerState.STOPPED


class DockerInterface(CoreSysAttributes):
    """Docker Supervisor interface."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self._meta: dict[str, Any] | None = None
        self.lock: asyncio.Lock = asyncio.Lock()

    @property
    def timeout(self) -> int:
        """Return timeout for Docker actions."""
        return 10

    @property
    def name(self) -> str | None:
        """Return name of Docker container."""
        return None

    @property
    def meta_config(self) -> dict[str, Any]:
        """Return meta data of configuration for container/image."""
        if not self._meta:
            return {}
        return self._meta.get("Config", {})

    @property
    def meta_host(self) -> dict[str, Any]:
        """Return meta data of configuration for host."""
        if not self._meta:
            return {}
        return self._meta.get("HostConfig", {})

    @property
    def meta_labels(self) -> dict[str, str]:
        """Return meta data of labels for container/image."""
        return self.meta_config.get("Labels") or {}

    @property
    def image(self) -> str | None:
        """Return name of Docker image."""
        try:
            return self.meta_config["Image"].partition(":")[0]
        except KeyError:
            return None

    @property
    def version(self) -> AwesomeVersion | None:
        """Return version of Docker image."""
        if LABEL_VERSION not in self.meta_labels:
            return None
        return AwesomeVersion(self.meta_labels[LABEL_VERSION])

    @property
    def arch(self) -> str | None:
        """Return arch of Docker image."""
        return self.meta_labels.get(LABEL_ARCH)

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.lock.locked()

    @property
    def restart_policy(self) -> RestartPolicy | None:
        """Return restart policy of container."""
        if "RestartPolicy" not in self.meta_host:
            return None

        policy = self.meta_host["RestartPolicy"].get("Name")
        return policy if policy else RestartPolicy.NO

    @property
    def security_opt(self) -> list[str]:
        """Control security options."""
        # Disable Seccomp / We don't support it official and it
        # causes problems on some types of host systems.
        return ["seccomp=unconfined"]

    def _get_credentials(self, image: str) -> dict:
        """Return a dictionay with credentials for docker login."""
        registry = None
        credentials = {}
        matcher = IMAGE_WITH_HOST.match(image)

        # Custom registry
        if matcher:
            if matcher.group(1) in self.sys_docker.config.registries:
                registry = matcher.group(1)
                credentials[ATTR_REGISTRY] = registry

        # If no match assume "dockerhub" as registry
        elif DOCKER_HUB in self.sys_docker.config.registries:
            registry = DOCKER_HUB

        if registry:
            stored = self.sys_docker.config.registries[registry]
            credentials[ATTR_USERNAME] = stored[ATTR_USERNAME]
            credentials[ATTR_PASSWORD] = stored[ATTR_PASSWORD]

            _LOGGER.debug(
                "Logging in to %s as %s",
                registry,
                stored[ATTR_USERNAME],
            )

        return credentials

    def _docker_login(self, image: str) -> None:
        """Try to log in to the registry if there are credentials available."""
        if not self.sys_docker.config.registries:
            return

        credentials = self._get_credentials(image)
        if not credentials:
            return

        self.sys_docker.docker.login(**credentials)

    @process_lock
    def install(
        self,
        version: AwesomeVersion,
        image: str | None = None,
        latest: bool = False,
        arch: CpuArch | None = None,
    ):
        """Pull docker image."""
        return self.sys_run_in_executor(self._install, version, image, latest, arch)

    def _install(
        self,
        version: AwesomeVersion,
        image: str | None = None,
        latest: bool = False,
        arch: CpuArch | None = None,
    ) -> None:
        """Pull Docker image.

        Need run inside executor.
        """
        image = image or self.image
        arch = arch or self.sys_arch.supervisor

        _LOGGER.info("Downloading docker image %s with tag %s.", image, version)
        try:
            if self.sys_docker.config.registries:
                # Try login if we have defined credentials
                self._docker_login(image)

            # Pull new image
            docker_image = self.sys_docker.images.pull(
                f"{image}:{version!s}",
                platform=MAP_ARCH[arch],
            )

            # Validate content
            try:
                self._validate_trust(docker_image.id, image, version)
            except CodeNotaryError:
                with suppress(docker.errors.DockerException):
                    self.sys_docker.images.remove(
                        image=f"{image}:{version!s}", force=True
                    )
                raise

            # Tag latest
            if latest:
                _LOGGER.info(
                    "Tagging image %s with version %s as latest", image, version
                )
                docker_image.tag(image, tag="latest")
        except docker.errors.APIError as err:
            if err.status_code == 429:
                self.sys_resolution.create_issue(
                    IssueType.DOCKER_RATELIMIT,
                    ContextType.SYSTEM,
                    suggestions=[SuggestionType.REGISTRY_LOGIN],
                )
                _LOGGER.info(
                    "Your IP address has made too many requests to Docker Hub which activated a rate limit. "
                    "For more details see https://www.home-assistant.io/more-info/dockerhub-rate-limit"
                )
            raise DockerError(
                f"Can't install {image}:{version!s}: {err}", _LOGGER.error
            ) from err
        except (docker.errors.DockerException, requests.RequestException) as err:
            capture_exception(err)
            raise DockerError(
                f"Unknown error with {image}:{version!s} -> {err!s}", _LOGGER.error
            ) from err
        except CodeNotaryUntrusted as err:
            raise DockerTrustError(
                f"Pulled image {image}:{version!s} failed on content-trust verification!",
                _LOGGER.critical,
            ) from err
        except CodeNotaryError as err:
            raise DockerTrustError(
                f"Error happened on Content-Trust check for {image}:{version!s}: {err!s}",
                _LOGGER.error,
            ) from err

        self._meta = docker_image.attrs

    def exists(self) -> Awaitable[bool]:
        """Return True if Docker image exists in local repository."""
        return self.sys_run_in_executor(self._exists)

    def _exists(self) -> bool:
        """Return True if Docker image exists in local repository.

        Need run inside executor.
        """
        with suppress(docker.errors.DockerException, requests.RequestException):
            self.sys_docker.images.get(f"{self.image}:{self.version!s}")
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
        except docker.errors.NotFound:
            return False
        except docker.errors.DockerException as err:
            raise DockerAPIError() from err
        except requests.RequestException as err:
            raise DockerRequestError() from err

        return docker_container.status == "running"

    def current_state(self) -> Awaitable[ContainerState]:
        """Return current state of container.

        Return a Future.
        """
        return self.sys_run_in_executor(self._current_state)

    def _current_state(self) -> ContainerState:
        """Return current state of container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.NotFound:
            return ContainerState.UNKNOWN
        except docker.errors.DockerException as err:
            raise DockerAPIError() from err
        except requests.RequestException as err:
            raise DockerRequestError() from err

        return _container_state_from_model(docker_container)

    @process_lock
    def attach(
        self, version: AwesomeVersion, *, skip_state_event_if_down: bool = False
    ) -> Awaitable[None]:
        """Attach to running Docker container."""
        return self.sys_run_in_executor(self._attach, version, skip_state_event_if_down)

    def _attach(
        self, version: AwesomeVersion, skip_state_event_if_down: bool = False
    ) -> None:
        """Attach to running docker container.

        Need run inside executor.
        """
        with suppress(docker.errors.DockerException, requests.RequestException):
            docker_container = self.sys_docker.containers.get(self.name)
            self._meta = docker_container.attrs
            self.sys_docker.monitor.watch_container(docker_container)

            state = _container_state_from_model(docker_container)
            if not (
                skip_state_event_if_down
                and state in [ContainerState.STOPPED, ContainerState.FAILED]
            ):
                # Fire event with current state of container
                self.sys_loop.call_soon_threadsafe(
                    self.sys_bus.fire_event,
                    BusEvent.DOCKER_CONTAINER_STATE_CHANGE,
                    DockerContainerStateEvent(
                        self.name, state, docker_container.id, int(time())
                    ),
                )

        with suppress(docker.errors.DockerException, requests.RequestException):
            if not self._meta and self.image:
                self._meta = self.sys_docker.images.get(
                    f"{self.image}:{version!s}"
                ).attrs

        # Successful?
        if not self._meta:
            raise DockerError()
        _LOGGER.info("Attaching to %s with version %s", self.image, self.version)

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
        except docker.errors.NotFound:
            return
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        if docker_container.status == "running":
            _LOGGER.info("Stopping %s application", self.name)
            with suppress(docker.errors.DockerException, requests.RequestException):
                docker_container.stop(timeout=self.timeout)

        if remove_container:
            with suppress(docker.errors.DockerException, requests.RequestException):
                _LOGGER.info("Cleaning %s application", self.name)
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
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"{self.name} not found for starting up", _LOGGER.error
            ) from err

        _LOGGER.info("Starting %s", self.name)
        try:
            docker_container.start()
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(f"Can't start {self.name}: {err}", _LOGGER.error) from err

    @process_lock
    def remove(self) -> Awaitable[None]:
        """Remove Docker images."""
        return self.sys_run_in_executor(self._remove)

    def _remove(self) -> None:
        """Remove docker images.

        Needs run inside executor.
        """
        # Cleanup container
        with suppress(DockerError):
            self._stop()

        _LOGGER.info("Removing image %s with latest and %s", self.image, self.version)

        try:
            with suppress(docker.errors.ImageNotFound):
                self.sys_docker.images.remove(image=f"{self.image}:latest", force=True)

            with suppress(docker.errors.ImageNotFound):
                self.sys_docker.images.remove(
                    image=f"{self.image}:{self.version!s}", force=True
                )

        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't remove image {self.image}: {err}", _LOGGER.warning
            ) from err

        self._meta = None

    @process_lock
    def update(
        self, version: AwesomeVersion, image: str | None = None, latest: bool = False
    ) -> Awaitable[None]:
        """Update a Docker image."""
        return self.sys_run_in_executor(self._update, version, image, latest)

    def _update(
        self, version: AwesomeVersion, image: str | None = None, latest: bool = False
    ) -> None:
        """Update a docker image.

        Need run inside executor.
        """
        image = image or self.image

        _LOGGER.info(
            "Updating image %s:%s to %s:%s", self.image, self.version, image, version
        )

        # Update docker image
        self._install(version, image=image, latest=latest)

        # Stop container & cleanup
        with suppress(DockerError):
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
        except (docker.errors.DockerException, requests.RequestException):
            return b""

        try:
            return docker_container.logs(tail=100, stdout=True, stderr=True)
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.warning("Can't grep logs from %s: %s", self.image, err)

        return b""

    @process_lock
    def cleanup(self, old_image: str | None = None) -> Awaitable[None]:
        """Check if old version exists and cleanup."""
        return self.sys_run_in_executor(self._cleanup, old_image)

    def _cleanup(self, old_image: str | None = None) -> None:
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            origin = self.sys_docker.images.get(f"{self.image}:{self.version!s}")
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't find {self.image} for cleanup", _LOGGER.warning
            ) from err

        # Cleanup Current
        try:
            images_list = self.sys_docker.images.list(name=self.image)
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Corrupt docker overlayfs found: {err}", _LOGGER.warning
            ) from err

        for image in images_list:
            if origin.id == image.id:
                continue

            with suppress(docker.errors.DockerException, requests.RequestException):
                _LOGGER.info("Cleanup images: %s", image.tags)
                self.sys_docker.images.remove(image.id, force=True)

        # Cleanup Old
        if not old_image or self.image == old_image:
            return

        try:
            images_list = self.sys_docker.images.list(name=old_image)
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Corrupt docker overlayfs found: {err}", _LOGGER.warning
            ) from err

        for image in images_list:
            if origin.id == image.id:
                continue

            with suppress(docker.errors.DockerException, requests.RequestException):
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
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        _LOGGER.info("Restarting %s", self.image)
        try:
            container.restart(timeout=self.timeout)
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't restart {self.image}: {err}", _LOGGER.warning
            ) from err

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
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # container is not running
        if docker_container.status != "running":
            raise DockerError(f"Container {self.name} is not running", _LOGGER.error)

        try:
            stats = docker_container.stats(stream=False)
            return DockerStats(stats)
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't read stats from {self.name}: {err}", _LOGGER.error
            ) from err

    def is_failed(self) -> Awaitable[bool]:
        """Return True if Docker is failing state.

        Return a Future.
        """
        return self.sys_run_in_executor(self._is_failed)

    def _is_failed(self) -> bool:
        """Return True if Docker is failing state.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.NotFound:
            return False
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # container is not running
        if docker_container.status != "exited":
            return False

        # Check return value
        return int(docker_container.attrs["State"]["ExitCode"]) != 0

    def get_latest_version(self) -> Awaitable[AwesomeVersion]:
        """Return latest version of local image."""
        return self.sys_run_in_executor(self._get_latest_version)

    def _get_latest_version(self) -> AwesomeVersion:
        """Return latest version of local image.

        Need run inside executor.
        """
        available_version: list[AwesomeVersion] = []
        try:
            for image in self.sys_docker.images.list(self.image):
                for tag in image.tags:
                    version = AwesomeVersion(tag.partition(":")[2])
                    if version.strategy == AwesomeVersionStrategy.UNKNOWN:
                        continue
                    available_version.append(version)

            if not available_version:
                raise ValueError()

        except (docker.errors.DockerException, ValueError) as err:
            raise DockerNotFound(
                f"No version found for {self.image}", _LOGGER.info
            ) from err
        except requests.RequestException as err:
            raise DockerRequestError(
                f"Communication issues with dockerd on Host: {err}", _LOGGER.warning
            ) from err

        _LOGGER.info("Found %s versions: %s", self.image, available_version)

        # Sort version and return latest version
        available_version.sort(reverse=True)
        return available_version[0]

    @process_lock
    def run_inside(self, command: str) -> Awaitable[CommandReturn]:
        """Execute a command inside Docker container."""
        return self.sys_run_in_executor(self._run_inside, command)

    def _run_inside(self, command: str) -> CommandReturn:
        """Execute a command inside Docker container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.NotFound:
            raise DockerNotFound() from None
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # Execute
        try:
            code, output = docker_container.exec_run(command)
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        return CommandReturn(code, output)

    def _validate_trust(
        self, image_id: str, image: str, version: AwesomeVersion
    ) -> None:
        """Validate trust of content."""
        checksum = image_id.partition(":")[2]
        job = asyncio.run_coroutine_threadsafe(
            self.sys_security.verify_own_content(checksum), self.sys_loop
        )
        job.result()

    @process_lock
    def check_trust(self) -> Awaitable[None]:
        """Check trust of exists Docker image."""
        return self.sys_run_in_executor(self._check_trust)

    def _check_trust(self) -> None:
        """Check trust of current image."""
        try:
            image = self.sys_docker.images.get(f"{self.image}:{self.version!s}")
        except (docker.errors.DockerException, requests.RequestException):
            return

        self._validate_trust(image.id, self.image, self.version)
