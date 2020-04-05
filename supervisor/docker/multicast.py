"""HA Cli docker object."""
from contextlib import suppress
import logging

from ..const import DOCKER_NETWORK_MASK, ENV_HASSIO_NETWORK, ENV_TIME
from ..coresys import CoreSysAttributes
from ..exceptions import DockerAPIError
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
            version=self.sys_plugins.multicast.version,
            init=False,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            network_mode="host",
            detach=True,
            extra_hosts={"supervisor": self.sys_docker.network.supervisor},
            environment={
                ENV_TIME: self.sys_timezone,
                ENV_HASSIO_NETWORK: str(DOCKER_NETWORK_MASK),
            },
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Start Multicast %s with version %s - Host", self.image, self.version
        )
