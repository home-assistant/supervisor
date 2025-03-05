"""Audio docker object."""

import logging

import docker
from docker.types import Mount

from ..const import DOCKER_CPU_RUNTIME_ALLOCATION
from ..coresys import CoreSysAttributes
from ..exceptions import DockerJobError
from ..hardware.const import PolicyGroup
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .const import (
    ENV_TIME,
    MOUNT_DBUS,
    MOUNT_DEV,
    MOUNT_MACHINE_ID,
    MOUNT_UDEV,
    PATH_PRIVATE_DATA,
    Capabilities,
    MountType,
)
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

AUDIO_DOCKER_NAME: str = "hassio_audio"


class DockerAudio(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for Supervisor Audio."""

    @property
    def image(self) -> str:
        """Return name of Supervisor Audio image."""
        return self.sys_plugins.audio.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return AUDIO_DOCKER_NAME

    @property
    def mounts(self) -> list[Mount]:
        """Return mounts for container."""
        mounts = [
            MOUNT_DEV,
            Mount(
                type=MountType.BIND,
                source=self.sys_config.path_extern_audio.as_posix(),
                target=PATH_PRIVATE_DATA.as_posix(),
                read_only=False,
            ),
            MOUNT_DBUS,
            MOUNT_UDEV,
        ]

        # Machine ID
        if self.sys_machine_id:
            mounts.append(MOUNT_MACHINE_ID)

        return mounts

    @property
    def cgroups_rules(self) -> list[str]:
        """Return a list of needed cgroups permission."""
        return self.sys_hardware.policy.get_cgroups_rules(
            PolicyGroup.AUDIO
        ) + self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.BLUETOOTH)

    @property
    def capabilities(self) -> list[Capabilities]:
        """Generate needed capabilities."""
        return [Capabilities.SYS_NICE, Capabilities.SYS_RESOURCE]

    @property
    def ulimits(self) -> list[docker.types.Ulimit]:
        """Generate ulimits for audio."""
        # Pulseaudio by default tries to use real-time scheduling with priority of 5.
        return [docker.types.Ulimit(name="rtprio", soft=10, hard=10)]

    @property
    def cpu_rt_runtime(self) -> int | None:
        """Limit CPU real-time runtime in microseconds."""
        if not self.sys_docker.info.support_cpu_realtime:
            return None
        return DOCKER_CPU_RUNTIME_ALLOCATION

    @Job(
        name="docker_audio_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        await self._run(
            tag=str(self.sys_plugins.audio.version),
            init=False,
            ipv4=self.sys_docker.network.audio,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            cap_add=self.capabilities,
            security_opt=self.security_opt,
            ulimits=self.ulimits,
            cpu_rt_runtime=self.cpu_rt_runtime,
            device_cgroup_rules=self.cgroups_rules,
            environment={
                ENV_TIME: self.sys_timezone,
            },
            mounts=self.mounts,
        )
        _LOGGER.info(
            "Starting Audio %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.audio,
        )
