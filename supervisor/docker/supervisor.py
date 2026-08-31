"""Init file for Supervisor Docker object."""

import asyncio
from ipaddress import IPv4Address
import logging
import os

import aiodocker
from awesomeversion.awesomeversion import AwesomeVersion

from ..exceptions import DockerError, DockerNotFound, DockerTimeoutError
from ..jobs.const import JobConcurrency
from ..jobs.decorator import Job
from .const import PropagationMode
from .interface import DockerInterface
from .utils import split_image_tag

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
        if not (container_metadata := await self._get_container()):
            raise DockerNotFound(
                f"Could not get supervisor container metadata for {self.name}"
            )
        self._meta = container_metadata

        _LOGGER.info(
            "Attaching to Supervisor %s with version %s",
            self.image,
            self.sys_supervisor.version,
        )

        container_id = self._meta["Id"]

        # If already attach
        if container_id in self.sys_docker.network.containers:
            return

        # Attach to network
        _LOGGER.info("Connecting Supervisor to hassio-network")
        await self.sys_docker.network.attach_container(
            container_id,
            self.name,
            alias=["supervisor"],
            ipv4=self.sys_docker.network.supervisor,
        )

    @Job(name="docker_supervisor_retag", concurrency=JobConcurrency.GROUP_QUEUE)
    async def retag(self) -> None:
        """Retag latest image to version."""
        if not (container_metadata := await self._get_container()):
            raise DockerNotFound(
                f"Could not get Supervisor container {self.name} for retag",
                _LOGGER.error,
            )

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
        except TimeoutError as err:
            raise DockerTimeoutError(
                "Timeout retagging Supervisor version", _LOGGER.error
            ) from err
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
        if not (container_metadata := await self._get_container()):
            raise DockerNotFound(
                f"Could not get container {self.name} to fix start tag", _LOGGER.error
            )

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
        except TimeoutError as err:
            raise DockerTimeoutError(
                "Timeout getting image metadata to fix start tag",
                _LOGGER.error,
            ) from err
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

                start_image, image_tag = split_image_tag(tag)
                start_tag = image_tag or "latest"

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

        except TimeoutError as err:
            raise DockerTimeoutError("Timeout fixing start tag", _LOGGER.error) from err
        except aiodocker.DockerError as err:
            raise DockerError(f"Can't fix start tag: {err}", _LOGGER.error) from err
