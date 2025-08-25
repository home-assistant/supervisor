"""Interface class for Supervisor Docker object."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Awaitable
from contextlib import suppress
import logging
import re
from time import time
from typing import Any, cast
from uuid import uuid4

from awesomeversion import AwesomeVersion
from awesomeversion.strategy import AwesomeVersionStrategy
import docker
from docker.models.containers import Container
from docker.models.images import Image
import requests

from ..bus import EventListener
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
    DockerLogOutOfOrder,
    DockerNotFound,
    DockerRequestError,
    DockerTrustError,
)
from ..jobs import SupervisorJob
from ..jobs.const import JOB_GROUP_DOCKER_INTERFACE, JobConcurrency
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.sentry import async_capture_exception
from .const import ContainerState, PullImageLayerStage, RestartPolicy
from .manager import CommandReturn, PullLogEntry
from .monitor import DockerContainerStateEvent
from .stats import DockerStats

_LOGGER: logging.Logger = logging.getLogger(__name__)

IMAGE_WITH_HOST = re.compile(r"^((?:[a-z0-9]+(?:-[a-z0-9]+)*\.)+[a-z]{2,})\/.+")
DOCKER_HUB = "hub.docker.com"

MAP_ARCH: dict[CpuArch | str, str] = {
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


class DockerInterface(JobGroup, ABC):
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
    @abstractmethod
    def name(self) -> str:
        """Return name of Docker container."""

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
        return self.active_job is not None

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

    def _process_pull_image_log(self, job_id: str, reference: PullLogEntry) -> None:
        """Process events fired from a docker while pulling an image, filtered to a given job id."""
        if (
            reference.job_id != job_id
            or not reference.id
            or not reference.status
            or not (stage := PullImageLayerStage.from_status(reference.status))
        ):
            return

        # Pulling FS Layer is our marker for a layer that needs to be downloaded and extracted. Otherwise it already exists and we can ignore
        job: SupervisorJob | None = None
        if stage == PullImageLayerStage.PULLING_FS_LAYER:
            job = self.sys_jobs.new_job(
                name="Pulling container image layer",
                initial_stage=stage.status,
                reference=reference.id,
                parent_id=job_id,
            )
            job.done = False
            return

        # Find our sub job to update details of
        for j in self.sys_jobs.jobs:
            if j.parent_id == job_id and j.reference == reference.id:
                job = j
                break

        # This likely only occurs if the logs came in out of sync and we got progress before the Pulling FS Layer one
        if not job:
            raise DockerLogOutOfOrder(
                f"Received pull image log with status {reference.status} for image id {reference.id} and parent job {job_id} but could not find a matching job, skipping",
                _LOGGER.debug,
            )

        # Hopefully these come in order but if they sometimes get out of sync, avoid accidentally going backwards
        # If it happens a lot though we may need to reconsider the value of this feature
        if job.done:
            raise DockerLogOutOfOrder(
                f"Received pull image log with status {reference.status} for job {job.uuid} but job was done, skipping",
                _LOGGER.debug,
            )

        if job.stage and stage < PullImageLayerStage.from_status(job.stage):
            raise DockerLogOutOfOrder(
                f"Received pull image log with status {reference.status} for job {job.uuid} but job was already on stage {job.stage}, skipping",
                _LOGGER.debug,
            )

        # For progress calcuation we assume downloading and extracting are each 50% of the time and others stages negligible
        progress = job.progress
        match stage:
            case PullImageLayerStage.DOWNLOADING | PullImageLayerStage.EXTRACTING:
                if (
                    reference.progress_detail
                    and reference.progress_detail.current
                    and reference.progress_detail.total
                ):
                    progress = 50 * (
                        reference.progress_detail.current
                        / reference.progress_detail.total
                    )
                    if stage == PullImageLayerStage.EXTRACTING:
                        progress += 50
            case (
                PullImageLayerStage.VERIFYING_CHECKSUM
                | PullImageLayerStage.DOWNLOAD_COMPLETE
            ):
                progress = 50
            case PullImageLayerStage.PULL_COMPLETE:
                progress = 100
            case PullImageLayerStage.RETRYING_DOWNLOAD:
                progress = 0

        if stage != PullImageLayerStage.RETRYING_DOWNLOAD and progress < job.progress:
            raise DockerLogOutOfOrder(
                f"Received pull image log with status {reference.status} for job {job.uuid} that implied progress was {progress} but current progress is {job.progress}, skipping",
                _LOGGER.debug,
            )

        # Our filters have all passed. Time to update the job
        # Only downloading and extracting have progress details. Use that to set extra
        # We'll leave it around on later stages as the total bytes may be useful after that stage
        if (
            stage in {PullImageLayerStage.DOWNLOADING, PullImageLayerStage.EXTRACTING}
            and reference.progress_detail
        ):
            job.update(
                progress=progress,
                stage=stage.status,
                extra={
                    "current": reference.progress_detail.current,
                    "total": reference.progress_detail.total,
                },
            )
        else:
            job.update(
                progress=progress,
                stage=stage.status,
                done=stage == PullImageLayerStage.PULL_COMPLETE,
                extra=None
                if stage == PullImageLayerStage.RETRYING_DOWNLOAD
                else job.extra,
            )

    @Job(
        name="docker_interface_install",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
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
        if not image:
            raise ValueError("Cannot pull without an image!")

        image_arch = str(arch) if arch else self.sys_arch.supervisor
        listener: EventListener | None = None

        _LOGGER.info("Downloading docker image %s with tag %s.", image, version)
        try:
            if self.sys_docker.config.registries:
                # Try login if we have defined credentials
                await self._docker_login(image)

            job_id = self.sys_jobs.current.uuid

            async def process_pull_image_log(reference: PullLogEntry) -> None:
                try:
                    self._process_pull_image_log(job_id, reference)
                except DockerLogOutOfOrder as err:
                    # Send all these to sentry. Missing a few progress updates
                    # shouldn't matter to users but matters to us
                    await async_capture_exception(err)

            listener = self.sys_bus.register_event(
                BusEvent.DOCKER_IMAGE_PULL_UPDATE, process_pull_image_log
            )

            # Pull new image
            docker_image = await self.sys_run_in_executor(
                self.sys_docker.pull_image,
                self.sys_jobs.current.uuid,
                image,
                str(version),
                platform=MAP_ARCH[image_arch],
            )

            # Validate content
            try:
                await self._validate_trust(cast(str, docker_image.id))
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
            await async_capture_exception(err)
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
        finally:
            if listener:
                self.sys_bus.remove_listener(listener)

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

    @Job(name="docker_interface_attach", concurrency=JobConcurrency.GROUP_QUEUE)
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
                        self.name, state, cast(str, docker_container.id), int(time())
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
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def run(self) -> None:
        """Run Docker image."""
        raise NotImplementedError()

    async def _run(self, **kwargs) -> None:
        """Run Docker image with retry inf necessary."""
        if await self.is_running():
            return

        # Cleanup
        await self.stop()

        # Create & Run container
        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.run, self.image, **kwargs
            )
        except DockerNotFound as err:
            # If image is missing, capture the exception as this shouldn't happen
            await async_capture_exception(err)
            raise

        # Store metadata
        self._meta = docker_container.attrs

    @Job(
        name="docker_interface_stop",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
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
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    def start(self) -> Awaitable[None]:
        """Start Docker container."""
        return self.sys_run_in_executor(self.sys_docker.start_container, self.name)

    @Job(
        name="docker_interface_remove",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def remove(self, *, remove_image: bool = True) -> None:
        """Remove Docker images."""
        # Cleanup container
        with suppress(DockerError):
            await self.stop()

        if remove_image:
            await self.sys_run_in_executor(
                self.sys_docker.remove_image, self.image, self.version
            )

        self._meta = None

    @Job(
        name="docker_interface_check_image",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def check_image(
        self,
        version: AwesomeVersion,
        expected_image: str,
        expected_cpu_arch: CpuArch | None = None,
    ) -> None:
        """Check we have expected image with correct arch."""
        expected_image_cpu_arch = (
            str(expected_cpu_arch) if expected_cpu_arch else self.sys_arch.supervisor
        )
        image_name = f"{expected_image}:{version!s}"
        if self.image == expected_image:
            try:
                image: Image = await self.sys_run_in_executor(
                    self.sys_docker.images.get, image_name
                )
            except (docker.errors.DockerException, requests.RequestException) as err:
                raise DockerError(
                    f"Could not get {image_name} for check due to: {err!s}",
                    _LOGGER.error,
                ) from err

            image_arch = f"{image.attrs['Os']}/{image.attrs['Architecture']}"
            if "Variant" in image.attrs:
                image_arch = f"{image_arch}/{image.attrs['Variant']}"

            # If we have an image and its the right arch, all set
            # It seems that newer Docker version return a variant for arm64 images.
            # Make sure we match linux/arm64 and linux/arm64/v8.
            expected_image_arch = MAP_ARCH[expected_image_cpu_arch]
            if image_arch.startswith(expected_image_arch):
                return
            _LOGGER.info(
                "Image %s has arch %s, expected %s. Reinstalling.",
                image_name,
                image_arch,
                expected_image_arch,
            )

        # We're missing the image we need. Stop and clean up what we have then pull the right one
        with suppress(DockerError):
            await self.remove()
        await self.install(version, expected_image, arch=expected_image_cpu_arch)

    @Job(
        name="docker_interface_update",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
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

    @Job(name="docker_interface_cleanup", concurrency=JobConcurrency.GROUP_QUEUE)
    async def cleanup(
        self,
        old_image: str | None = None,
        image: str | None = None,
        version: AwesomeVersion | None = None,
    ) -> None:
        """Check if old version exists and cleanup."""
        await self.sys_run_in_executor(
            self.sys_docker.cleanup_old_images,
            image or self.image,
            version or self.version,
            {old_image} if old_image else None,
        )

    @Job(
        name="docker_interface_restart",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    def restart(self) -> Awaitable[None]:
        """Restart docker container."""
        return self.sys_run_in_executor(
            self.sys_docker.restart_container, self.name, self.timeout
        )

    @Job(
        name="docker_interface_execute_command",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
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
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    def run_inside(self, command: str) -> Awaitable[CommandReturn]:
        """Execute a command inside Docker container."""
        return self.sys_run_in_executor(
            self.sys_docker.container_run_inside, self.name, command
        )

    async def _validate_trust(self, image_id: str) -> None:
        """Validate trust of content."""
        checksum = image_id.partition(":")[2]
        return await self.sys_security.verify_own_content(checksum)

    @Job(
        name="docker_interface_check_trust",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def check_trust(self) -> None:
        """Check trust of exists Docker image."""
        try:
            image = await self.sys_run_in_executor(
                self.sys_docker.images.get, f"{self.image}:{self.version!s}"
            )
        except (docker.errors.DockerException, requests.RequestException):
            return

        await self._validate_trust(cast(str, image.id))
