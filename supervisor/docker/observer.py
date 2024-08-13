"""Observer docker object."""

import logging

from ..const import DOCKER_NETWORK_MASK
from ..coresys import CoreSysAttributes
from ..exceptions import DockerJobError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .const import ENV_TIME, ENV_TOKEN, MOUNT_DOCKER, RestartPolicy
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

OBSERVER_DOCKER_NAME: str = "hassio_observer"
ENV_NETWORK_MASK: str = "NETWORK_MASK"


class DockerObserver(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for observer plugin."""

    @property
    def image(self):
        """Return name of observer image."""
        return self.sys_plugins.observer.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return OBSERVER_DOCKER_NAME

    @Job(
        name="docker_observer_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        await self._run(
            tag=str(self.sys_plugins.observer.version),
            init=False,
            ipv4=self.sys_docker.network.observer,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            security_opt=self.security_opt,
            restart_policy={"Name": RestartPolicy.ALWAYS},
            extra_hosts={"supervisor": self.sys_docker.network.supervisor},
            environment={
                ENV_TIME: self.sys_timezone,
                ENV_TOKEN: self.sys_plugins.observer.supervisor_token,
                ENV_NETWORK_MASK: DOCKER_NETWORK_MASK,
            },
            mounts=[MOUNT_DOCKER],
            ports={"80/tcp": 4357},
            oom_score_adj=-300,
        )
        _LOGGER.info(
            "Starting Observer %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.observer,
        )
