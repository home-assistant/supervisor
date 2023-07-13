"""Init file for Supervisor Docker object."""
from collections.abc import Awaitable
from ipaddress import IPv4Address
import logging

from awesomeversion import AwesomeVersion, AwesomeVersionCompareException
import docker
from docker.types import Mount
import requests

from ..const import LABEL_MACHINE, MACHINE_ID
from ..exceptions import DockerError
from ..hardware.const import PolicyGroup
from ..homeassistant.const import LANDINGPAGE
from ..utils import process_lock
from .const import (
    ENV_TIME,
    ENV_TOKEN,
    ENV_TOKEN_OLD,
    MOUNT_DBUS,
    MOUNT_DEV,
    MOUNT_MACHINE_ID,
    MOUNT_UDEV,
    MountType,
    PropagationMode,
)
from .interface import CommandReturn, DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)
_VERIFY_TRUST: AwesomeVersion = AwesomeVersion("2021.5.0")
_HASS_DOCKER_NAME: str = "homeassistant"


class DockerHomeAssistant(DockerInterface):
    """Docker Supervisor wrapper for Home Assistant."""

    @property
    def machine(self) -> str | None:
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
        return _HASS_DOCKER_NAME

    @property
    def timeout(self) -> int:
        """Return timeout for Docker actions."""
        # Synchronized homeassistant's S6_SERVICES_GRACETIME
        # to avoid killing Home Assistant Core
        return 220 + 20

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP address of this container."""
        return self.sys_docker.network.gateway

    @property
    def cgroups_rules(self) -> list[str]:
        """Return a list of needed cgroups permission."""
        return (
            self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.UART)
            + self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.VIDEO)
            + self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.GPIO)
            + self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.USB)
        )

    @property
    def mounts(self) -> list[Mount]:
        """Return mounts for container."""
        mounts = [
            MOUNT_DEV,
            MOUNT_DBUS,
            MOUNT_UDEV,
            # Add folders
            Mount(
                type=MountType.BIND.value,
                source=self.sys_config.path_extern_homeassistant.as_posix(),
                target="/config",
                read_only=False,
            ),
            Mount(
                type=MountType.BIND.value,
                source=self.sys_config.path_extern_ssl.as_posix(),
                target="/ssl",
                read_only=True,
            ),
            Mount(
                type=MountType.BIND.value,
                source=self.sys_config.path_extern_share.as_posix(),
                target="/share",
                read_only=False,
                propagation=PropagationMode.RSLAVE.value,
            ),
            Mount(
                type=MountType.BIND.value,
                source=self.sys_config.path_extern_media.as_posix(),
                target="/media",
                read_only=False,
                propagation=PropagationMode.RSLAVE.value,
            ),
            # Configuration audio
            Mount(
                type=MountType.BIND.value,
                source=self.sys_homeassistant.path_extern_pulse.as_posix(),
                target="/etc/pulse/client.conf",
                read_only=True,
            ),
            Mount(
                type=MountType.BIND.value,
                source=self.sys_plugins.audio.path_extern_pulse.as_posix(),
                target="/run/audio",
                read_only=True,
            ),
            Mount(
                type=MountType.BIND.value,
                source=self.sys_plugins.audio.path_extern_asound.as_posix(),
                target="/etc/asound.conf",
                read_only=True,
            ),
        ]

        # Machine ID
        if MACHINE_ID.exists():
            mounts.append(MOUNT_MACHINE_ID)

        return mounts

    async def _run(self) -> None:
        """Run Docker image."""
        if await self.is_running():
            return

        # Cleanup
        await self._stop()

        # Create & Run container
        docker_container = await self.sys_run_in_executor(
            self.sys_docker.run,
            self.image,
            tag=(self.sys_homeassistant.version),
            name=self.name,
            hostname=self.name,
            detach=True,
            privileged=True,
            init=False,
            security_opt=self.security_opt,
            network_mode="host",
            mounts=self.mounts,
            device_cgroup_rules=self.cgroups_rules,
            extra_hosts={
                "supervisor": self.sys_docker.network.supervisor,
                "observer": self.sys_docker.network.observer,
            },
            environment={
                "SUPERVISOR": self.sys_docker.network.supervisor,
                "HASSIO": self.sys_docker.network.supervisor,
                ENV_TIME: self.sys_timezone,
                ENV_TOKEN: self.sys_homeassistant.supervisor_token,
                ENV_TOKEN_OLD: self.sys_homeassistant.supervisor_token,
            },
            tmpfs={"/tmp": ""},
            oom_score_adj=-300,
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Starting Home Assistant %s with version %s", self.image, self.version
        )

    @process_lock
    async def execute_command(self, command: str) -> CommandReturn:
        """Create a temporary container and run command."""
        return await self.sys_run_in_executor(
            self.sys_docker.run_command,
            self.image,
            version=self.sys_homeassistant.version,
            command=command,
            privileged=True,
            init=True,
            entrypoint=[],
            detach=True,
            stdout=True,
            stderr=True,
            mounts=[
                Mount(
                    type=MountType.BIND.value,
                    source=self.sys_config.path_extern_homeassistant.as_posix(),
                    target="/config",
                    read_only=False,
                ),
                Mount(
                    type=MountType.BIND.value,
                    source=self.sys_config.path_extern_ssl.as_posix(),
                    target="/ssl",
                    read_only=True,
                ),
                Mount(
                    type=MountType.BIND.value,
                    source=self.sys_config.path_extern_share.as_posix(),
                    target="/share",
                    read_only=False,
                ),
            ],
            environment={ENV_TIME: self.sys_timezone},
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
            return DockerError()

        # we run on an old image, stop and start it
        if docker_container.image.id != docker_image.id:
            return False

        # Check of correct state
        if docker_container.status not in ("exited", "running", "created"):
            return False

        return True

    async def _validate_trust(
        self, image_id: str, image: str, version: AwesomeVersion
    ) -> None:
        """Validate trust of content."""
        try:
            if version != LANDINGPAGE and version < _VERIFY_TRUST:
                return
        except AwesomeVersionCompareException:
            return

        await super()._validate_trust(image_id, image, version)
