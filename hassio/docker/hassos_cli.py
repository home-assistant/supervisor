"""HassOS Cli docker object."""
import logging
import os

import docker

from .interface import DockerInterface
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class DockerHassOSCli(DockerInterface, CoreSysAttributes):
    """Docker hassio wrapper for HassOS Cli."""

    @property
    def image(self):
        """Return name of HassOS cli image."""
        return f"homeassistant/{self.sys_arch}-hassio-cli"

    def _attach(self):
        """Attach to running docker container.
        Need run inside executor.
        """
        try:
            image = self.sys_docker.images.get(self.image)
        except docker.errors.DockerException:
            return False

        self._meta = image.attrs
        _LOGGER.info("Attach to HassOS cli %s with version %s",
                     self.image, self.version)

        return True
