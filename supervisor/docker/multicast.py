"""HA Cli docker object."""

import logging

from ..coresys import CoreSysAttributes
from ..exceptions import DockerJobError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .const import ENV_TIME, Capabilities
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

MULTICAST_DOCKER_NAME: str = "hassio_multicast"


class DockerMulticast(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for HA multicast."""

    @property
    def image(self):
        """Return name of HA multicast image."""
        return self.sys_plugins.multicast.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return MULTICAST_DOCKER_NAME

    @property
    def capabilities(self) -> list[Capabilities]:
        """Generate needed capabilities."""
        return [Capabilities.NET_ADMIN]

    @Job(
        name="docker_multicast_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        await self._run(
            tag=str(self.sys_plugins.multicast.version),
            init=False,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            network_mode="host",
            detach=True,
            security_opt=self.security_opt,
            cap_add=self.capabilities,
            extra_hosts={"supervisor": self.sys_docker.network.supervisor},
            environment={ENV_TIME: self.sys_timezone},
        )
        _LOGGER.info(
            "Starting Multicast %s with version %s - Host", self.image, self.version
        )
