"""Interface class for Supervisor Docker object."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Awaitable
from contextlib import suppress
from http import HTTPStatus
import logging
from time import time
from typing import Any, cast
from uuid import uuid4

import aiodocker
from awesomeversion import AwesomeVersion
from awesomeversion.strategy import AwesomeVersionStrategy
import docker
from docker.models.containers import Container
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
    DockerAPIError,
    DockerError,
    DockerHubRateLimitExceeded,
    DockerJobError,
    DockerLogOutOfOrder,
    DockerNotFound,
    DockerRequestError,
)
from ..jobs import SupervisorJob
from ..jobs.const import JOB_GROUP_DOCKER_INTERFACE, JobConcurrency
from ..jobs.decorator import Job
from ..jobs.job_group import JobGroup
from ..resolution.const import ContextType, IssueType, SuggestionType
from ..utils.sentry import async_capture_exception
from .const import DOCKER_HUB, ContainerState, PullImageLayerStage, RestartPolicy
from .manager import CommandReturn, PullLogEntry
from .monitor import DockerContainerStateEvent
from .stats import DockerStats

_LOGGER: logging.Logger = logging.getLogger(__name__)

MAP_ARCH: dict[CpuArch, str] = {
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
        """Return a dictionary with credentials for docker login."""
        credentials = {}
        registry = self.sys_docker.config.get_registry_for_image(image)

        if registry:
            stored = self.sys_docker.config.registries[registry]
            credentials[ATTR_USERNAME] = stored[ATTR_USERNAME]
            credentials[ATTR_PASSWORD] = stored[ATTR_PASSWORD]
            if registry != DOCKER_HUB:
                credentials[ATTR_REGISTRY] = registry

            _LOGGER.debug(
                "Logging in to %s as %s",
                registry,
                stored[ATTR_USERNAME],
            )

        return credentials

    def _process_pull_image_log(  # noqa: C901
        self, install_job_id: str, reference: PullLogEntry
    ) -> None:
        """Process events fired from a docker while pulling an image, filtered to a given job id."""
        if (
            reference.job_id != install_job_id
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
                parent_id=install_job_id,
                internal=True,
            )
            job.done = False
            return

        # Find our sub job to update details of
        for j in self.sys_jobs.jobs:
            if j.parent_id == install_job_id and j.reference == reference.id:
                job = j
                break

        # There should no longer be any real risk of logs out of order anymore.
        # However tests with very small images have shown that sometimes Docker
        # skips stages in log. So keeping this one as a safety check on null job
        if not job:
            raise DockerLogOutOfOrder(
                f"Received pull image log with status {reference.status} for image id {reference.id} and parent job {install_job_id} but could not find a matching job, skipping",
                _LOGGER.debug,
            )

        # For progress calculation we assume downloading is 70% of time, extracting is 30% and others stages negligible
        progress = job.progress
        match stage:
            case PullImageLayerStage.DOWNLOADING | PullImageLayerStage.EXTRACTING:
                if (
                    reference.progress_detail
                    and reference.progress_detail.current
                    and reference.progress_detail.total
                ):
                    progress = (
                        reference.progress_detail.current
                        / reference.progress_detail.total
                    )
                    if stage == PullImageLayerStage.DOWNLOADING:
                        progress = 70 * progress
                    else:
                        progress = 70 + 30 * progress
            case (
                PullImageLayerStage.VERIFYING_CHECKSUM
                | PullImageLayerStage.DOWNLOAD_COMPLETE
            ):
                progress = 70
            case PullImageLayerStage.PULL_COMPLETE:
                progress = 100
            case PullImageLayerStage.RETRYING_DOWNLOAD:
                progress = 0

        # No real risk of getting things out of order in current implementation
        # but keeping this one in case another change to these trips us up.
        if stage != PullImageLayerStage.RETRYING_DOWNLOAD and progress < job.progress:
            raise DockerLogOutOfOrder(
                f"Received pull image log with status {reference.status} for job {job.uuid} that implied progress was {progress} but current progress is {job.progress}, skipping",
                _LOGGER.debug,
            )

        # Our filters have all passed. Time to update the job
        # Only downloading and extracting have progress details. Use that to set extra
        # We'll leave it around on later stages as the total bytes may be useful after that stage
        # Enforce range to prevent float drift error
        progress = max(0, min(progress, 100))
        if (
            stage in {PullImageLayerStage.DOWNLOADING, PullImageLayerStage.EXTRACTING}
            and reference.progress_detail
            and reference.progress_detail.current is not None
            and reference.progress_detail.total is not None
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
            # If we reach DOWNLOAD_COMPLETE without ever having set extra (small layers that skip
            # the downloading phase), set a minimal extra so aggregate progress calculation can proceed
            extra = job.extra
            if stage == PullImageLayerStage.DOWNLOAD_COMPLETE and not job.extra:
                extra = {"current": 1, "total": 1}

            job.update(
                progress=progress,
                stage=stage.status,
                done=stage == PullImageLayerStage.PULL_COMPLETE,
                extra=None if stage == PullImageLayerStage.RETRYING_DOWNLOAD else extra,
            )

        # Once we have received a progress update for every child job, start to set status of the main one
        install_job = self.sys_jobs.get_job(install_job_id)
        layer_jobs = [
            job
            for job in self.sys_jobs.jobs
            if job.parent_id == install_job.uuid
            and job.name == "Pulling container image layer"
        ]

        # First set the total bytes to be downloaded/extracted on the main job
        if not install_job.extra:
            total = 0
            for job in layer_jobs:
                if not job.extra:
                    return
                total += job.extra["total"]
            install_job.extra = {"total": total}
        else:
            total = install_job.extra["total"]

        # Then determine total progress based on progress of each sub-job, factoring in size of each compared to total
        progress = 0.0
        stage = PullImageLayerStage.PULL_COMPLETE
        for job in layer_jobs:
            if not job.extra or not job.extra.get("total"):
                return
            progress += job.progress * (job.extra["total"] / total)
            job_stage = PullImageLayerStage.from_status(cast(str, job.stage))

            if job_stage < PullImageLayerStage.EXTRACTING:
                stage = PullImageLayerStage.DOWNLOADING
            elif (
                stage == PullImageLayerStage.PULL_COMPLETE
                and job_stage < PullImageLayerStage.PULL_COMPLETE
            ):
                stage = PullImageLayerStage.EXTRACTING

        # Ensure progress is 100 at this point to prevent float drift
        if stage == PullImageLayerStage.PULL_COMPLETE:
            progress = 100

        # To reduce noise, limit updates to when result has changed by an entire percent or when stage changed
        if stage != install_job.stage or progress >= install_job.progress + 1:
            install_job.update(stage=stage.status, progress=max(0, min(progress, 100)))

    @Job(
        name="docker_interface_install",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
        internal=True,
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

        image_arch = arch or self.sys_arch.supervisor
        listener: EventListener | None = None

        _LOGGER.info("Downloading docker image %s with tag %s.", image, version)
        try:
            # Get credentials for private registries to pass to aiodocker
            credentials = self._get_credentials(image) or None

            curr_job_id = self.sys_jobs.current.uuid

            async def process_pull_image_log(reference: PullLogEntry) -> None:
                try:
                    self._process_pull_image_log(curr_job_id, reference)
                except DockerLogOutOfOrder as err:
                    # Send all these to sentry. Missing a few progress updates
                    # shouldn't matter to users but matters to us
                    await async_capture_exception(err)

            listener = self.sys_bus.register_event(
                BusEvent.DOCKER_IMAGE_PULL_UPDATE, process_pull_image_log
            )

            # Pull new image, passing credentials to aiodocker
            docker_image = await self.sys_docker.pull_image(
                self.sys_jobs.current.uuid,
                image,
                str(version),
                platform=MAP_ARCH[image_arch],
                auth=credentials,
            )

            # Tag latest
            if latest:
                _LOGGER.info(
                    "Tagging image %s with version %s as latest", image, version
                )
                await self.sys_docker.images.tag(
                    docker_image["Id"], image, tag="latest"
                )
        except docker.errors.APIError as err:
            if err.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                self.sys_resolution.create_issue(
                    IssueType.DOCKER_RATELIMIT,
                    ContextType.SYSTEM,
                    suggestions=[SuggestionType.REGISTRY_LOGIN],
                )
                raise DockerHubRateLimitExceeded(_LOGGER.error) from err
            await async_capture_exception(err)
            raise DockerError(
                f"Can't install {image}:{version!s}: {err}", _LOGGER.error
            ) from err
        except aiodocker.DockerError as err:
            if err.status == HTTPStatus.TOO_MANY_REQUESTS:
                self.sys_resolution.create_issue(
                    IssueType.DOCKER_RATELIMIT,
                    ContextType.SYSTEM,
                    suggestions=[SuggestionType.REGISTRY_LOGIN],
                )
                raise DockerHubRateLimitExceeded(_LOGGER.error) from err
            await async_capture_exception(err)
            raise DockerError(
                f"Can't install {image}:{version!s}: {err}", _LOGGER.error
            ) from err
        except (
            docker.errors.DockerException,
            requests.RequestException,
        ) as err:
            await async_capture_exception(err)
            raise DockerError(
                f"Unknown error with {image}:{version!s} -> {err!s}", _LOGGER.error
            ) from err
        finally:
            if listener:
                self.sys_bus.remove_listener(listener)

        self._meta = docker_image

    async def exists(self) -> bool:
        """Return True if Docker image exists in local repository."""
        with suppress(aiodocker.DockerError, requests.RequestException):
            await self.sys_docker.images.inspect(f"{self.image}:{self.version!s}")
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

        with suppress(aiodocker.DockerError, requests.RequestException):
            if not self._meta and self.image:
                self._meta = await self.sys_docker.images.inspect(
                    f"{self.image}:{version!s}"
                )

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
        if not self.image or not self.version:
            raise DockerError(
                "Cannot determine image and/or version from metadata!", _LOGGER.error
            )

        # Cleanup container
        with suppress(DockerError):
            await self.stop()

        if remove_image:
            await self.sys_docker.remove_image(self.image, self.version)

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
        arch = expected_cpu_arch or self.sys_arch.supervisor
        image_name = f"{expected_image}:{version!s}"
        if self.image == expected_image:
            try:
                image = await self.sys_docker.images.inspect(image_name)
            except (aiodocker.DockerError, requests.RequestException) as err:
                raise DockerError(
                    f"Could not get {image_name} for check due to: {err!s}",
                    _LOGGER.error,
                ) from err

            image_arch = f"{image['Os']}/{image['Architecture']}"
            if "Variant" in image:
                image_arch = f"{image_arch}/{image['Variant']}"

            # If we have an image and its the right arch, all set
            # It seems that newer Docker version return a variant for arm64 images.
            # Make sure we match linux/arm64 and linux/arm64/v8.
            expected_image_arch = MAP_ARCH[arch]
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
        await self.install(version, expected_image, arch=arch)

    @Job(
        name="docker_interface_update",
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
    )
    async def update(
        self,
        version: AwesomeVersion,
        image: str | None = None,
        latest: bool = False,
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
        if not (use_image := image or self.image):
            raise DockerError("Cannot determine image from metadata!", _LOGGER.error)
        if not (use_version := version or self.version):
            raise DockerError("Cannot determine version from metadata!", _LOGGER.error)

        await self.sys_docker.cleanup_old_images(
            use_image, use_version, {old_image} if old_image else None
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
            for image in await self.sys_docker.images.list(
                filters=f'{{"reference": ["{self.image}"]}}'
            ):
                for tag in image["RepoTags"]:
                    version = AwesomeVersion(tag.partition(":")[2])
                    if version.strategy == AwesomeVersionStrategy.UNKNOWN:
                        continue
                    available_version.append(version)

            if not available_version:
                raise ValueError()

        except (aiodocker.DockerError, ValueError) as err:
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
