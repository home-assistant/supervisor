"""HA Cli docker object."""
import logging

import docker

from ..coresys import CoreSysAttributes
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DockerCli(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for HA cli."""

    @property
    def image(self):
        """Return name of HA cli image."""
        return f"homeassistant/{self.sys_arch.supervisor}-hassio-cli"

    def _stop(self, remove_container=True):
        """Don't need stop."""
        return True

    def _attach(self, tag: str):
        """Attach to running Docker container.

        Need run inside executor.
        """
        try:
            image = self.sys_docker.images.get(f"{self.image}:{tag}")
        except docker.errors.DockerException:
            _LOGGER.warning("Can't find a HA cli %s", self.image)
        else:
            self._meta = image.attrs
            _LOGGER.info("Found HA cli %s with version %s", self.image, self.version)
