"""Init file for Hass.io Docker object."""
from ipaddress import IPv4Address
import logging
import os
from typing import Awaitable

import docker

from ..coresys import CoreSysAttributes
from ..exceptions import DockerAPIError
from .interface import DockerInterface

_LOGGER = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface, CoreSysAttributes):
    """Docker Hass.io wrapper for Supervisor."""

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return os.environ["SUPERVISOR_NAME"]

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP address of this container."""
        return self.sys_docker.network.supervisor

    def _attach(self, tag: str) -> None:
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
        except docker.errors.DockerException:
            raise DockerAPIError() from None

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Attach to Supervisor %s with version %s", self.image, self.version
        )

        # If already attach
        if docker_container in self.sys_docker.network.containers:
            return

        # Attach to network
        _LOGGER.info("Connect Supervisor to Hass.io Network")
        self.sys_docker.network.attach_container(
            docker_container, alias=["hassio"], ipv4=self.sys_docker.network.supervisor
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

            docker_container.image.tag(self.image, tag=self.version)
            docker_container.image.tag(self.image, tag="latest")
        except docker.errors.DockerException as err:
            _LOGGER.error("Can't retag supervisor version: %s", err)
            raise DockerAPIError() from None
