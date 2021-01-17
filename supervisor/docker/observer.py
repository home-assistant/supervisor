"""Observer docker object."""
import logging

from ..const import DOCKER_NETWORK_MASK, ENV_TIME, ENV_TOKEN
from ..coresys import CoreSysAttributes
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

    def _run(self) -> None:
        """Run Docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # Cleanup
        self._stop()

        # Create & Run container
        docker_container = self.sys_docker.run(
            self.image,
            tag=str(self.sys_plugins.observer.version),
            init=False,
            ipv4=self.sys_docker.network.observer,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            restart_policy={"Name": "always"},
            extra_hosts={"supervisor": self.sys_docker.network.supervisor},
            environment={
                ENV_TIME: self.sys_config.timezone,
                ENV_TOKEN: self.sys_plugins.observer.supervisor_token,
                ENV_NETWORK_MASK: DOCKER_NETWORK_MASK,
            },
            volumes={"/run/docker.sock": {"bind": "/run/docker.sock", "mode": "ro"}},
            ports={"80/tcp": 4357},
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Starting Observer %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.observer,
        )
