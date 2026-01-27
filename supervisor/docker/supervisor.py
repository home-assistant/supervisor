"""Init file for Supervisor Docker object."""

import asyncio
from ipaddress import IPv4Address
import logging
import os

import aiodocker
from awesomeversion.awesomeversion import AwesomeVersion

from ..exceptions import DockerError
from ..jobs.const import JobConcurrency
from ..jobs.decorator import Job
from .const import PropagationMode
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface):
    """Docker Supervisor wrapper for Supervisor."""

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return os.environ["SUPERVISOR_NAME"]

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP address of this container."""
        return self.sys_docker.network.supervisor

    @property
    def privileged(self) -> bool:
        """Return True if the container run with Privileged."""
        return self.meta_host.get("Privileged", False)

    @property
    def host_mounts_available(self) -> bool:
        """Return True if container can see mounts on host within its data directory."""
        return self._meta is not None and any(
            mount.get("Propagation") == PropagationMode.SLAVE
            for mount in self.meta_mounts
            if mount.get("Destination") == "/data"
        )

    @Job(name="docker_supervisor_attach", concurrency=JobConcurrency.GROUP_QUEUE)
    async def attach(
        self, version: AwesomeVersion, *, skip_state_event_if_down: bool = False
    ) -> None:
        """Attach to running docker container."""
        try:
            docker_container = await self.sys_docker.containers.get(self.name)
            self._meta = await docker_container.show()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Could not get supervisor container metadata: {err!s}"
            ) from err

        _LOGGER.info(
            "Attaching to Supervisor %s with version %s",
            self.image,
            self.sys_supervisor.version,
        )

        # If already attach
        if docker_container.id in self.sys_docker.network.containers:
            return

        # Attach to network
        _LOGGER.info("Connecting Supervisor to hassio-network")
        await self.sys_run_in_executor(
            self.sys_docker.network.attach_container,
            docker_container.id,
            self.name,
            alias=["supervisor"],
            ipv4=self.sys_docker.network.supervisor,
        )

    @Job(name="docker_supervisor_retag", concurrency=JobConcurrency.GROUP_QUEUE)
    async def retag(self) -> None:
        """Retag latest image to version."""
        try:
            docker_container = await self.sys_docker.containers.get(self.name)
            container_metadata = await docker_container.show()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Could not get Supervisor container for retag: {err}", _LOGGER.error
            ) from err

        # See https://github.com/docker/docker-py/blob/df3f8e2abc5a03de482e37214dddef9e0cee1bb1/docker/models/containers.py#L41
        metadata_image = container_metadata.get("ImageID", container_metadata["Image"])
        if not self.image or not metadata_image:
            raise DockerError(
                "Could not locate image from container metadata for retag",
                _LOGGER.error,
            )

        try:
            await asyncio.gather(
                self.sys_docker.images.tag(
                    metadata_image, self.image, tag=str(self.version)
                ),
                self.sys_docker.images.tag(metadata_image, self.image, tag="latest"),
            )
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't retag Supervisor version: {err}", _LOGGER.error
            ) from err

    @Job(
        name="docker_supervisor_update_start_tag",
        concurrency=JobConcurrency.GROUP_QUEUE,
    )
    async def update_start_tag(self, image: str, version: AwesomeVersion) -> None:
        """Update start tag to new version."""
        try:
            docker_container = await self.sys_docker.containers.get(self.name)
            container_metadata = await docker_container.show()
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't get container to fix start tag: {err}", _LOGGER.error
            ) from err

        # See https://github.com/docker/docker-py/blob/df3f8e2abc5a03de482e37214dddef9e0cee1bb1/docker/models/containers.py#L41
        metadata_image = container_metadata.get("ImageID", container_metadata["Image"])
        if not metadata_image:
            raise DockerError(
                "Cannot locate image from container metadata to fix start tag",
                _LOGGER.error,
            )

        try:
            container_image, new_image = await asyncio.gather(
                self.sys_docker.images.inspect(metadata_image),
                self.sys_docker.images.inspect(f"{image}:{version!s}"),
            )
        except aiodocker.DockerError as err:
            raise DockerError(
                f"Can't get image metadata to fix start tag: {err}", _LOGGER.error
            ) from err

        try:
            # Find start tag
            for tag in container_image["RepoTags"]:
                # See https://github.com/docker/docker-py/blob/df3f8e2abc5a03de482e37214dddef9e0cee1bb1/docker/models/images.py#L47
                if tag == "<none>:<none>":
                    continue

                start_image = tag.partition(":")[0]
                start_tag = tag.partition(":")[2] or "latest"

                # If version tag
                if start_tag != "latest":
                    continue
                await asyncio.gather(
                    self.sys_docker.images.tag(
                        new_image["Id"], start_image, tag=start_tag
                    ),
                    self.sys_docker.images.tag(
                        new_image["Id"], start_image, tag=version.string
                    ),
                )

        except aiodocker.DockerError as err:
            raise DockerError(f"Can't fix start tag: {err}", _LOGGER.error) from err
