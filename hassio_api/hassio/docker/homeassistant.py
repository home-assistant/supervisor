"""Init file for HassIO docker object."""
import asyncio

import docker

import . from DockerBase
from ..const.py import HOMEASSISTANT_CONFIG, HOMEASSISTANT_SSL, HASSIO_DOCKER

_LOGGER = logging.getLogger(__name__)
HASS_DOCKER_NAME = 'homeassistant'

class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def _run():
        """Run docker image.

        Need run inside executor.
        """
        try:
            self.container = self.dock.containers.run(
                self.image,
                name=HASS_DOCKER_NAME,
                remove=True,
                network_mode='host',
                restart_policy={
                    "Name": "always",
                    "MaximumRetryCount": 10,
                },
                links={HASSIO_DOCKER: 'HASSIO'},
                volumes={
                    HOMEASSISTANT_CONFIG: {'bind': '/config', 'mode': 'rw'},
                    HOMEASSISTANT_SSL: {'bind': '/ssl', 'mode': 'rw'},
                })
        except docker.errors.APIError as err:
            _LOGGER.error("Can't run %s", self.image)
            return False

        return True
