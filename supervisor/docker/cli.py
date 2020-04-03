"""HA Cli docker object."""
from contextlib import suppress
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import DockerAPIError
from .interface import DockerInterface
from ..const import ENV_TIME, ENV_TOKEN

_LOGGER: logging.Logger = logging.getLogger(__name__)

CLI_DOCKER_NAME: str = "hassio_cli"


class DockerCli(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for HA cli."""

    @property
    def image(self):
        """Return name of HA cli image."""
        return self.sys_cli.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return CLI_DOCKER_NAME

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
            entrypoint=["/init"],
            command=["/bin/bash", "-c", "sleep infinity"],
            version=self.sys_cli.version,
            init=False,
            ipv4=self.sys_docker.network.cli,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            extra_hosts={"supervisor": self.sys_docker.network.supervisor},
            environment={
                ENV_TIME: self.sys_timezone,
                ENV_TOKEN: self.sys_cli.supervisor_token,
            },
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Start CLI %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.audio,
        )
