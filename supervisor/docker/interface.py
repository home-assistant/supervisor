"""Interface class for Supervisor Docker object."""
import asyncio
from contextlib import suppress
import logging
import re
from typing import Any, Awaitable, Dict, List, Optional

from awesomeversion import AwesomeVersion
from awesomeversion.strategy import AwesomeVersionStrategy
import docker
import requests

from . import CommandReturn
from ..const import (
    ATTR_PASSWORD,
    ATTR_REGISTRY,
    ATTR_USERNAME,
    LABEL_ARCH,
    LABEL_VERSION,
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
from .stats import DockerStats

_LOGGER: logging.Logger = logging.getLogger(__name__)

IMAGE_WITH_HOST = re.compile(r"^((?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,})\/.+")
DOCKER_HUB = "hub.docker.com"


class DockerInterface(CoreSysAttributes):
    """Docker Supervisor interface."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        self.coresys: CoreSys = coresys
        self._meta: Optional[Dict[str, Any]] = None
        self.lock: asyncio.Lock = asyncio.Lock()

    @property
    def timeout(self) -> int:
        """Return timeout for Docker actions."""
        return 10

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
    def version(self) -> Optional[AwesomeVersion]:
        """Return version of Docker image."""
        if LABEL_VERSION not in self.meta_labels:
            return None
        return AwesomeVersion(self.meta_labels[LABEL_VERSION])

    @property
    def arch(self) -> Optional[str]:
        """Return arch of Docker image."""
        return self.meta_labels.get(LABEL_ARCH)

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.lock.locked()

    @property
    def security_opt(self) -> List[str]:
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
        self, version: AwesomeVersion, image: Optional[str] = None, latest: bool = False
    ):
        """Pull docker image."""
        return self.sys_run_in_executor(self._install, version, image, latest)

    def _install(
        self, version: AwesomeVersion, image: Optional[str] = None, latest: bool = False
    ) -> None:
        """Pull Docker image.

        Need run inside executor.
        """
        image = image or self.image

        _LOGGER.info("Downloading docker image %s with tag %s.", image, version)
        try:
            if self.sys_docker.config.registries:
                # Try login if we have defined credentials
                self._docker_login(image)

            # Pull new image
            docker_image = self.sys_docker.images.pull(f"{image}:{version!s}")

            # Validate content
            try:
                self._validate_trust(docker_image.id)
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
            _LOGGER.error("Can't install %s:%s -> %s.", image, version, err)
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
            raise DockerError() from err
        except (docker.errors.DockerException, requests.RequestException) as err:
            self.sys_capture_exception(err)
            raise DockerError(
                f"Unknown error with {image}:{version} -> {err!s}", _LOGGER.error
            ) from err
        except CodeNotaryUntrusted as err:
            raise DockerTrustError(
                f"Pulled image {image}:{version} failed on content-trust verification!",
                _LOGGER.critical,
            ) from err
        except CodeNotaryError as err:
            raise DockerTrustError(
                f"Error happened on Content-Trust check for {image}:{version}: {err!s}",
                _LOGGER.error,
            ) from err
        else:
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

    @process_lock
    def attach(self, version: AwesomeVersion):
        """Attach to running Docker container."""
        return self.sys_run_in_executor(self._attach, version)

    def _attach(self, version: AwesomeVersion) -> None:
        """Attach to running docker container.

        Need run inside executor.
        """
        with suppress(docker.errors.DockerException, requests.RequestException):
            self._meta = self.sys_docker.containers.get(self.name).attrs

        with suppress(docker.errors.DockerException, requests.RequestException):
            if not self._meta and self.image:
                self._meta = self.sys_docker.images.get(
                    f"{self.image}:{version!s}"
                ).attrs

        # Successfull?
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
            _LOGGER.error("%s not found for starting up", self.name)
            raise DockerError() from err

        _LOGGER.info("Starting %s", self.name)
        try:
            docker_container.start()
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Can't start %s: %s", self.name, err)
            raise DockerError() from err

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
            _LOGGER.warning("Can't remove image %s: %s", self.image, err)
            raise DockerError() from err

        self._meta = None

    @process_lock
    def update(
        self, version: AwesomeVersion, image: Optional[str] = None, latest: bool = False
    ) -> Awaitable[None]:
        """Update a Docker image."""
        return self.sys_run_in_executor(self._update, version, image, latest)

    def _update(
        self, version: AwesomeVersion, image: Optional[str] = None, latest: bool = False
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
    def cleanup(self, old_image: Optional[str] = None) -> Awaitable[None]:
        """Check if old version exists and cleanup."""
        return self.sys_run_in_executor(self._cleanup, old_image)

    def _cleanup(self, old_image: Optional[str] = None) -> None:
        """Check if old version exists and cleanup.

        Need run inside executor.
        """
        try:
            origin = self.sys_docker.images.get(f"{self.image}:{self.version!s}")
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.warning("Can't find %s for cleanup", self.image)
            raise DockerError() from err

        # Cleanup Current
        try:
            images_list = self.sys_docker.images.list(name=self.image)
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.warning("Corrupt docker overlayfs found: %s", err)
            raise DockerError() from err

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
            _LOGGER.warning("Corrupt docker overlayfs found: %s", err)
            raise DockerError() from err

        for image in images_list:
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
            _LOGGER.warning("Can't restart %s: %s", self.image, err)
            raise DockerError() from err

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

        try:
            stats = docker_container.stats(stream=False)
            return DockerStats(stats)
        except (docker.errors.DockerException, requests.RequestException) as err:
            _LOGGER.error("Can't read stats from %s: %s", self.name, err)
            raise DockerError() from err

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
        available_version: List[AwesomeVersion] = []
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
            _LOGGER.info("No version found for %s", self.image)
            raise DockerNotFound() from err
        except requests.RequestException as err:
            _LOGGER.warning("Communication issues with dockerd on Host: %s", err)
            raise DockerRequestError() from err
        else:
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

    def _validate_trust(self, image_id: str) -> None:
        """Validate trust of content."""
        checksum = image_id.partition(":")[2]
        job = asyncio.run_coroutine_threadsafe(
            self.sys_verify_content(checksum=checksum), self.sys_loop
        )
        job.result(timeout=20)
