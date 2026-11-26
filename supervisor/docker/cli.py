"""HA Cli docker object."""

import logging

from ..const import CLI_DOCKER_NAME, SOCKET_NAME_SUPERVISOR
from ..coresys import CoreSysAttributes
from ..exceptions import DockerJobError
from ..jobs.const import JobConcurrency
from ..jobs.decorator import Job
from .const import (
    ENV_SUPERVISOR_SOCKET,
    ENV_TIME,
    ENV_TOKEN,
    PATH_RUN_API,
    DockerMount,
    MountType,
)
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


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
        on_condition=DockerJobError,
        concurrency=JobConcurrency.GROUP_REJECT,
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
            mounts=[
                # The cli shares the host OS socket, both act as the host OS
                DockerMount(
                    type=MountType.BIND,
                    source=self.sys_host.path_extern_run_supervisor.as_posix(),
                    target=PATH_RUN_API.as_posix(),
                    read_only=True,
                ),
            ],
            environment={
                ENV_TIME: self.sys_timezone,
                ENV_SUPERVISOR_SOCKET: (
                    PATH_RUN_API / SOCKET_NAME_SUPERVISOR
                ).as_posix(),
                # Images with a ha older than 5.7.0 only know the token
                ENV_TOKEN: self.sys_plugins.cli.supervisor_token,
            },
        )
        _LOGGER.info(
            "Starting CLI %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.cli,
        )
