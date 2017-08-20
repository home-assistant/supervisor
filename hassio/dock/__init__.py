"""Init file for HassIO docker object."""
import asyncio
import logging

import docker

from ..const import SOCKET_DOCKER

_LOGGER = logging.getLogger(__name__)


class DockerBase(object):
    """Docker hassio wrapper."""

    def __init__(self, config, loop):
        """Initialize docker base wrapper."""
        self.config = config
        self.loop = loop
        self.dock = docker.DockerClient(
            base_url="unix:/{}".format(str(SOCKET_DOCKER)), version='auto')

    @property
    def images(self):
        """Return api images."""
        return self.dock.images

    @property
    def containers(self):
        """Return api containers."""
        return self.dock.containers

    @property
    def api(self):
        """Return api containers."""
        return self.dock.api
