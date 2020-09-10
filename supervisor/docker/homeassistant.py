"""Init file for Supervisor Docker object."""
from ipaddress import IPv4Address
import logging
from typing import Awaitable, Dict, Optional

import docker
import requests

from ..const import (
    ENV_OBSERVER,
    ENV_TIME,
    ENV_TOKEN,
    ENV_TOKEN_OLD,
    LABEL_MACHINE,
    MACHINE_ID,
)
from ..exceptions import DockerAPIError
from .interface import CommandReturn, DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

HASS_DOCKER_NAME = "homeassistant"


class DockerHomeAssistant(DockerInterface):
    """Docker Supervisor wrapper for Home Assistant."""

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

    @property
    def volumes(self) -> Dict[str, Dict[str, str]]:
        """Return Volumes for the mount."""
        volumes = {"/run/dbus": {"bind": "/run/dbus", "mode": "ro"}}

        # Add folders
        volumes.update(
            {
                str(self.sys_config.path_extern_homeassistant): {
                    "bind": "/config",
                    "mode": "rw",
                },
                str(self.sys_config.path_extern_ssl): {"bind": "/ssl", "mode": "ro"},
                str(self.sys_config.path_extern_share): {
                    "bind": "/share",
                    "mode": "rw",
                },
                str(self.sys_config.path_extern_media): {
                    "bind": "/media",
                    "mode": "rw",
                },
            }
        )

        # Machine ID
        if MACHINE_ID.exists():
            volumes.update({str(MACHINE_ID): {"bind": str(MACHINE_ID), "mode": "ro"}})

        # Configuration Audio
        volumes.update(
            {
                str(self.sys_homeassistant.path_extern_pulse): {
                    "bind": "/etc/pulse/client.conf",
                    "mode": "ro",
                },
                str(self.sys_plugins.audio.path_extern_pulse): {
                    "bind": "/run/audio",
                    "mode": "ro",
                },
                str(self.sys_plugins.audio.path_extern_asound): {
                    "bind": "/etc/asound.conf",
                    "mode": "ro",
                },
            }
        )

        return volumes

    def _run(self) -> None:
        """Run Docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # Cleanup
        self._stop()

        # Create & Run container
        docker_container = self.sys_docker.run(
            self.image,
            version=self.sys_homeassistant.version,
            name=self.name,
            hostname=self.name,
            detach=True,
            privileged=True,
            init=False,
            network_mode="host",
            volumes=self.volumes,
            extra_hosts={
                "supervisor": self.sys_docker.network.supervisor,
                "observer": self.sys_docker.network.observer,
            },
            environment={
                "HASSIO": self.sys_docker.network.supervisor,
                "SUPERVISOR": self.sys_docker.network.supervisor,
                ENV_TIME: self.sys_config.timezone,
                ENV_TOKEN: self.sys_homeassistant.supervisor_token,
                ENV_TOKEN_OLD: self.sys_homeassistant.supervisor_token,
                ENV_OBSERVER: self.sys_plugins.observer.access_token,
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
            entrypoint=[],
            detach=True,
            stdout=True,
            stderr=True,
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
            environment={ENV_TIME: self.sys_config.timezone},
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
            docker_image = self.sys_docker.images.get(
                f"{self.image}:{self.sys_homeassistant.version}"
            )
        except docker.errors.NotFound:
            return False
        except (docker.errors.DockerException, requests.RequestException):
            return DockerAPIError()

        # we run on an old image, stop and start it
        if docker_container.image.id != docker_image.id:
            return False

        return True
