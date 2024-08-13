"""HA Cli docker object."""

import logging

from ..coresys import CoreSysAttributes
from ..exceptions import DockerJobError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from .const import ENV_TIME, ENV_TOKEN
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

CLI_DOCKER_NAME: str = "hassio_cli"


class DockerCli(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for HA cli."""

    @property
    def image(self):
        """Return name of HA cli image."""
        return self.sys_plugins.cli.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return CLI_DOCKER_NAME

    @Job(
        name="docker_cli_run",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=DockerJobError,
    )
    async def run(self) -> None:
        """Run Docker image."""
        await self._run(
            entrypoint=["/init"],
            tag=str(self.sys_plugins.cli.version),
            init=False,
            ipv4=self.sys_docker.network.cli,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            security_opt=self.security_opt,
            extra_hosts={
                "supervisor": self.sys_docker.network.supervisor,
                "observer": self.sys_docker.network.observer,
            },
            environment={
                ENV_TIME: self.sys_timezone,
                ENV_TOKEN: self.sys_plugins.cli.supervisor_token,
            },
        )
        _LOGGER.info(
            "Starting CLI %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.cli,
        )
