"""DNS docker object."""

import logging

from docker.types import Mount

from ..coresys import CoreSysAttributes
from ..exceptions import DockerJobError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .const import ENV_TIME, MOUNT_DBUS, MountType
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

DNS_DOCKER_NAME: str = "hassio_dns"


class DockerDNS(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for Supervisor DNS."""

    @property
    def image(self) -> str:
        """Return name of Supervisor DNS image."""
        return self.sys_plugins.dns.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return DNS_DOCKER_NAME

    @Job(
        name="docker_dns_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        await self._run(
            tag=str(self.sys_plugins.dns.version),
            init=False,
            dns=False,
            ipv4=self.sys_docker.network.dns,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            security_opt=self.security_opt,
            environment={ENV_TIME: self.sys_timezone},
            mounts=[
                Mount(
                    type=MountType.BIND,
                    source=self.sys_config.path_extern_dns.as_posix(),
                    target="/config",
                    read_only=False,
                ),
                MOUNT_DBUS,
            ],
            oom_score_adj=-300,
        )
        _LOGGER.info(
            "Starting DNS %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.dns,
        )
