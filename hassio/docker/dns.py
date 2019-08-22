"""HassOS Cli docker object."""
from contextlib import suppress
import logging

from ..const import ENV_TIME
from ..coresys import CoreSysAttributes
from ..exceptions import DockerAPIError
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

DNS_DOCKER_NAME: str = "hassio_dns"


class DockerDNS(DockerInterface, CoreSysAttributes):
    """Docker Hass.io wrapper for Hass.io DNS."""

    @property
    def image(self) -> str:
        """Return name of Hass.io DNS image."""
        return f"homeassistant/{self.sys_arch.supervisor}-hassio-dns"

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
            ipv4=self.sys_docker.network.dns,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            init=True,
            environment={ENV_TIME: self.sys_timezone},
            volumes={
                str(self.sys_config.path_extern_dns): {"bind": "/config", "mode": "ro"}
            },
        )

        self._meta = docker_container.attrs
        _LOGGER.info("Start DNS %s with version %s", self.image, self.version)
