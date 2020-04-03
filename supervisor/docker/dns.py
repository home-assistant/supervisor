"""DNS docker object."""
from contextlib import suppress
import logging

from ..const import ENV_TIME
from ..coresys import CoreSysAttributes
from ..exceptions import DockerAPIError
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

DNS_DOCKER_NAME: str = "hassio_dns"


class DockerDNS(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for Supervisor DNS."""

    @property
    def image(self) -> str:
        """Return name of Supervisor DNS image."""
        return self.sys_dns.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return DNS_DOCKER_NAME

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
            version=self.sys_dns.version,
            init=False,
            dns=False,
            ipv4=self.sys_docker.network.dns,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            environment={ENV_TIME: self.sys_timezone},
            volumes={
                str(self.sys_config.path_extern_dns): {"bind": "/config", "mode": "ro"}
            },
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Start DNS %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.dns,
        )
