"""Interface class for Supervisor Docker object."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Awaitable
from contextlib import suppress
import logging
import re
from time import time
from typing import Any
from uuid import uuid4

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
from ..coresys import CoreSys
from ..exceptions import (
    CodeNotaryError,
    CodeNotaryUntrusted,
    DockerAPIError,
    DockerError,
    DockerJobError,
    DockerNotFound,
    DockerRequestError,
    DockerTrustError,
)
from ..jobs.const import JOB_GROUP_DOCKER_INTERFACE, JobExecutionLimit
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..resolution.const import ContextType, IssueType, SuggestionType
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


class DockerInterface(JobGroup):
    """Docker Supervisor interface."""

    def __init__(self, coresys: CoreSys):
        """Initialize Docker base wrapper."""
        super().__init__(
            coresys,
            JOB_GROUP_DOCKER_INTERFACE.format_map(
                defaultdict(str, name=self.name or uuid4().hex)
            ),
            self.name,
        )
        self.coresys: CoreSys = coresys
        self._meta: dict[str, Any] | None = None

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
    def meta_mounts(self) -> list[dict[str, Any]]:
        """Return meta data of mounts for container/image."""
        if not self._meta:
            return []
        return self._meta.get("Mounts", [])

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
        return self.active_job

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

    @property
    def healthcheck(self) -> dict[str, Any] | None:
        """Healthcheck of instance if it has one."""
        return self.meta_config.get("Healthcheck")

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

    async def _docker_login(self, image: str) -> None:
        """Try to log in to the registry if there are credentials available."""
        if not self.sys_docker.config.registries:
            return

        credentials = self._get_credentials(image)
        if not credentials:
            return

        await self.sys_run_in_executor(self.sys_docker.docker.login, **credentials)

    @Job(
        name="docker_interface_install",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def install(
        self,
        version: AwesomeVersion,
        image: str | None = None,
        latest: bool = False,
        arch: CpuArch | None = None,
    ) -> None:
        """Pull docker image."""
        image = image or self.image
        arch = arch or self.sys_arch.supervisor

        _LOGGER.info("Downloading docker image %s with tag %s.", image, version)
        try:
            if self.sys_docker.config.registries:
                # Try login if we have defined credentials
                await self._docker_login(image)

            # Pull new image
            docker_image = await self.sys_run_in_executor(
                self.sys_docker.images.pull,
                f"{image}:{version!s}",
                platform=MAP_ARCH[arch],
            )

            # Validate content
            try:
                await self._validate_trust(docker_image.id, image, version)
            except CodeNotaryError:
                with suppress(docker.errors.DockerException):
                    await self.sys_run_in_executor(
                        self.sys_docker.images.remove,
                        image=f"{image}:{version!s}",
                        force=True,
                    )
                raise

            # Tag latest
            if latest:
                _LOGGER.info(
                    "Tagging image %s with version %s as latest", image, version
                )
                await self.sys_run_in_executor(docker_image.tag, image, tag="latest")
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

    async def exists(self) -> bool:
        """Return True if Docker image exists in local repository."""
        with suppress(docker.errors.DockerException, requests.RequestException):
            await self.sys_run_in_executor(
                self.sys_docker.images.get, f"{self.image}:{self.version!s}"
            )
            return True
        return False

    async def is_running(self) -> bool:
        """Return True if Docker is running."""
        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.containers.get, self.name
            )
        except docker.errors.NotFound:
            return False
        except docker.errors.DockerException as err:
            raise DockerAPIError() from err
        except requests.RequestException as err:
            raise DockerRequestError() from err

        return docker_container.status == "running"

    async def current_state(self) -> ContainerState:
        """Return current state of container."""
        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.containers.get, self.name
            )
        except docker.errors.NotFound:
            return ContainerState.UNKNOWN
        except docker.errors.DockerException as err:
            raise DockerAPIError() from err
        except requests.RequestException as err:
            raise DockerRequestError() from err

        return _container_state_from_model(docker_container)

    @Job(name="docker_interface_attach", limit=JobExecutionLimit.GROUP_WAIT)
    async def attach(
        self, version: AwesomeVersion, *, skip_state_event_if_down: bool = False
    ) -> None:
        """Attach to running Docker container."""
        with suppress(docker.errors.DockerException, requests.RequestException):
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.containers.get, self.name
            )
            self._meta = docker_container.attrs
            self.sys_docker.monitor.watch_container(docker_container)

            state = _container_state_from_model(docker_container)
            if not (
                skip_state_event_if_down
                and state in [ContainerState.STOPPED, ContainerState.FAILED]
            ):
                # Fire event with current state of container
                self.sys_bus.fire_event(
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

    @Job(
        name="docker_interface_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        raise NotImplementedError()

    @Job(
        name="docker_interface_stop",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def stop(self, remove_container: bool = True) -> None:
        """Stop/remove Docker container."""
        with suppress(DockerNotFound):
            await self.sys_run_in_executor(
                self.sys_docker.stop_container,
                self.name,
                self.timeout,
                remove_container,
            )

    @Job(
        name="docker_interface_start",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    def start(self) -> Awaitable[None]:
        """Start Docker container."""
        return self.sys_run_in_executor(self.sys_docker.start_container, self.name)

    @Job(
        name="docker_interface_remove",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def remove(self) -> None:
        """Remove Docker images."""
        # Cleanup container
        with suppress(DockerError):
            await self.stop()

        await self.sys_run_in_executor(
            self.sys_docker.remove_image, self.image, self.version
        )
        self._meta = None

    @Job(
        name="docker_interface_update",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def update(
        self, version: AwesomeVersion, image: str | None = None, latest: bool = False
    ) -> None:
        """Update a Docker image."""
        image = image or self.image

        _LOGGER.info(
            "Updating image %s:%s to %s:%s", self.image, self.version, image, version
        )

        # Update docker image
        await self.install(version, image=image, latest=latest)

        # Stop container & cleanup
        with suppress(DockerError):
            await self.stop()

    async def logs(self) -> bytes:
        """Return Docker logs of container."""
        with suppress(DockerError):
            return await self.sys_run_in_executor(
                self.sys_docker.container_logs, self.name
            )

        return b""

    @Job(name="docker_interface_cleanup", limit=JobExecutionLimit.GROUP_WAIT)
    def cleanup(
        self,
        old_image: str | None = None,
        image: str | None = None,
        version: AwesomeVersion | None = None,
    ) -> Awaitable[None]:
        """Check if old version exists and cleanup."""
        return self.sys_run_in_executor(
            self.sys_docker.cleanup_old_images,
            image or self.image,
            version or self.version,
            {old_image} if old_image else None,
        )

    @Job(
        name="docker_interface_restart",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    def restart(self) -> Awaitable[None]:
        """Restart docker container."""
        return self.sys_run_in_executor(
            self.sys_docker.restart_container, self.name, self.timeout
        )

    @Job(
        name="docker_interface_execute_command",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def execute_command(self, command: str) -> CommandReturn:
        """Create a temporary container and run command."""
        raise NotImplementedError()

    async def stats(self) -> DockerStats:
        """Read and return stats from container."""
        stats = await self.sys_run_in_executor(
            self.sys_docker.container_stats, self.name
        )
        return DockerStats(stats)

    async def is_failed(self) -> bool:
        """Return True if Docker is failing state."""
        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.containers.get, self.name
            )
        except docker.errors.NotFound:
            return False
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        # container is not running
        if docker_container.status != "exited":
            return False

        # Check return value
        return int(docker_container.attrs["State"]["ExitCode"]) != 0

    async def get_latest_version(self) -> AwesomeVersion:
        """Return latest version of local image."""
        available_version: list[AwesomeVersion] = []
        try:
            for image in await self.sys_run_in_executor(
                self.sys_docker.images.list, self.image
            ):
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

    @Job(
        name="docker_interface_run_inside",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    def run_inside(self, command: str) -> Awaitable[CommandReturn]:
        """Execute a command inside Docker container."""
        return self.sys_run_in_executor(
            self.sys_docker.container_run_inside, self.name, command
        )

    async def _validate_trust(
        self, image_id: str, image: str, version: AwesomeVersion
    ) -> None:
        """Validate trust of content."""
        checksum = image_id.partition(":")[2]
        return await self.sys_security.verify_own_content(checksum)

    @Job(
        name="docker_interface_check_trust",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def check_trust(self) -> None:
        """Check trust of exists Docker image."""
        try:
            image = await self.sys_run_in_executor(
                self.sys_docker.images.get, f"{self.image}:{self.version!s}"
            )
        except (docker.errors.DockerException, requests.RequestException):
            return

        await self._validate_trust(image.id, self.image, self.version)
