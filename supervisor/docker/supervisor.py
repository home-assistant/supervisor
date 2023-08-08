"""Init file for Supervisor Docker object."""
from collections.abc import Awaitable
from ipaddress import IPv4Address
import logging
import os

from awesomeversion.awesomeversion import AwesomeVersion
import docker
import requests

from ..coresys import CoreSysAttributes
from ..exceptions import DockerError, DockerJobError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .const import PropagationMode
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface, CoreSysAttributes):
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
        return self._meta and any(
            mount.get("Propagation") == PropagationMode.SLAVE.value
            for mount in self.meta_mounts
            if mount.get("Destination") == "/data"
        )

    @Job(limit=JobExecutionLimit.GROUP_ONCE, on_condition=DockerJobError)
    async def attach(
        self, version: AwesomeVersion, *, skip_state_event_if_down: bool = False
    ) -> None:
        """Attach to running docker container."""
        try:
            docker_container = await self.sys_run_in_executor(
                self.sys_docker.containers.get, self.name
            )
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError() from err

        self._meta = docker_container.attrs
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
            docker_container,
            alias=["supervisor"],
            ipv4=self.sys_docker.network.supervisor,
        )

    def retag(self) -> Awaitable[None]:
        """Retag latest image to version."""
        return self.sys_run_in_executor(self._retag)

    def _retag(self) -> None:
        """Retag latest image to version.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)

            docker_container.image.tag(self.image, tag=str(self.version))
            docker_container.image.tag(self.image, tag="latest")
        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(
                f"Can't retag Supervisor version: {err}", _LOGGER.error
            ) from err

    def update_start_tag(self, image: str, version: AwesomeVersion) -> Awaitable[None]:
        """Update start tag to new version."""
        return self.sys_run_in_executor(self._update_start_tag, image, version)

    def _update_start_tag(self, image: str, version: AwesomeVersion) -> None:
        """Update start tag to new version.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
            docker_image = self.sys_docker.images.get(f"{image}:{version!s}")

            # Find start tag
            for tag in docker_container.image.tags:
                start_image = tag.partition(":")[0]
                start_tag = tag.partition(":")[2] or "latest"

                # If version tag
                if start_tag != "latest":
                    continue
                docker_image.tag(start_image, start_tag)
                docker_image.tag(start_image, version.string)

        except (docker.errors.DockerException, requests.RequestException) as err:
            raise DockerError(f"Can't fix start tag: {err}", _LOGGER.error) from err
