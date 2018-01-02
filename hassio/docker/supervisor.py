"""Init file for HassIO docker object."""
import logging
import os

import docker

from .interface import DockerInterface
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class DockerSupervisor(DockerInterface, CoreSysAttributes):
    """Docker hassio wrapper for HomeAssistant."""

    @property
    def name(self):
        """Return name of docker container."""
        return os.environ['SUPERVISOR_NAME']

    def _attach(self):
        """Attach to running docker container.

        Need run inside executor.
        """
        try:
            container = self._docker.containers.get(self.name)
        except docker.errors.DockerException:
            return False

        self._meta = container.attrs
        _LOGGER.info("Attach to supervisor %s with version %s",
                     self.image, self.version)

        # if already attach
        if container in self._docker.network.containers:
            return True

        # attach to network
        return self._docker.network.attach_container(
            container, alias=['hassio'], ipv4=self._docker.network.supervisor)
