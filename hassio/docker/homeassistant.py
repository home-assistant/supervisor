"""Init file for Hass.io Docker object."""
from distutils.version import StrictVersion
from contextlib import suppress
from ipaddress import IPv4Address
import logging
import re
from typing import Awaitable, List, Optional

import docker

from ..const import ENV_TIME, ENV_TOKEN, LABEL_MACHINE
from ..exceptions import DockerAPIError
from .interface import CommandReturn, DockerInterface

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = "homeassistant"
RE_VERSION = re.compile(r"(?P<version>\d+\.\d+\.\d+(?:b\d+|d\d+)?)")


class DockerHomeAssistant(DockerInterface):
    """Docker Hass.io wrapper for Home Assistant."""

    @property
    def machine(self) -> Optional[str]:
        """Return machine of Home Assistant Docker image."""
        if self._meta and LABEL_MACHINE in self._meta["Config"]["Labels"]:
            return self._meta["Config"]["Labels"][LABEL_MACHINE]
        return None

    @property
    def image(self) -> str:
        """Return name of Docker image."""
        return self.sys_homeassistant.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return HASS_DOCKER_NAME

    @property
    def timeout(self) -> int:
        """Return timeout for Docker actions."""
        return 60

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP address of this container."""
        return self.sys_docker.network.gateway

    def _run(self) -> None:
        """Run Docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # Cleanup
        with suppress(DockerAPIError):
            self._stop()

        # Create & Run container
        docker_container = self.sys_docker.run(
            self.image,
            version=self.sys_homeassistant.version,
            name=self.name,
            hostname=self.name,
            detach=True,
            privileged=True,
            init=True,
            network_mode="host",
            environment={
                "HASSIO": self.sys_docker.network.supervisor,
                ENV_TIME: self.sys_timezone,
                ENV_TOKEN: self.sys_homeassistant.hassio_token,
            },
            volumes={
                str(self.sys_config.path_extern_homeassistant): {
                    "bind": "/config",
                    "mode": "rw",
                },
                str(self.sys_config.path_extern_ssl): {"bind": "/ssl", "mode": "ro"},
                str(self.sys_config.path_extern_share): {
                    "bind": "/share",
                    "mode": "rw",
                },
            },
        )

        self._meta = docker_container.attrs
        _LOGGER.info("Start homeassistant %s with version %s", self.image, self.version)

    def _execute_command(self, command: str) -> CommandReturn:
        """Create a temporary container and run command.

        Need run inside executor.
        """
        return self.sys_docker.run_command(
            self.image,
            version=self.sys_homeassistant.version,
            command=command,
            privileged=True,
            init=True,
            detach=True,
            stdout=True,
            stderr=True,
            environment={ENV_TIME: self.sys_timezone},
            volumes={
                str(self.sys_config.path_extern_homeassistant): {
                    "bind": "/config",
                    "mode": "rw",
                },
                str(self.sys_config.path_extern_ssl): {"bind": "/ssl", "mode": "ro"},
                str(self.sys_config.path_extern_share): {
                    "bind": "/share",
                    "mode": "ro",
                },
            },
        )

    def is_initialize(self) -> Awaitable[bool]:
        """Return True if Docker container exists."""
        return self.sys_run_in_executor(self._is_initialize)

    def _is_initialize(self) -> bool:
        """Return True if docker container exists.

        Need run inside executor.
        """
        try:
            docker_container = self.sys_docker.containers.get(self.name)
            docker_image = self.sys_docker.images.get(self.image)
        except docker.errors.DockerException:
            return False

        # we run on an old image, stop and start it
        if docker_container.image.id != docker_image.id:
            return False

        return True

    def get_latest_version(self) -> Awaitable[str]:
        """Return latest version of local Home Asssistant image."""
        return self.sys_run_in_executor(self._get_latest_version)

    def _get_latest_version(self) -> str:
        """Return latest version of local Home Asssistant image.

        Need run inside executor.
        """
        available_version: List[str] = []
        try:
            for image in self.sys_docker.images.list(self.image):
                for tag in image.tags:
                    match = RE_VERSION.search(tag)
                    if not match:
                        continue
                    available_version.append(match.group("version"))

            assert available_version

        except (docker.errors.DockerException, AssertionError):
            _LOGGER.warning("No local HA version found")
            raise DockerAPIError()
        else:
            _LOGGER.debug("Found HA versions: %s", available_version)

        # Sort version and return latest version
        available_version.sort(key=StrictVersion, reverse=True)
        return available_version[0]
