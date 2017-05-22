"""Init file for HassIO docker object."""
import logging

import docker

from . import DockerBase

_LOGGER = logging.getLogger(__name__)

HASS_DOCKER_NAME = 'homeassistant'


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def __init__(self, config, loop, dock):
        """Initialize docker homeassistant wrapper."""
        super().__init__(config, loop, dock, image=config.homeassistant_image)

    @property
    def docker_name(self):
        """Return name of docker container."""
        return HASS_DOCKER_NAME

    def _run(self):
        """Run docker image.

        Need run inside executor.
        """
        if self._is_running():
            return

        # cleanup old container
        self._stop()

        try:
            self.container = self.dock.containers.run(
                self.image,
                name=self.docker_name,
                detach=True,
                privileged=True,
                network_mode='host',
                environment={
                    'HASSIO': self.config.api_endpoint,
                    'TZ': self.config.timezone,
                },
                volumes={
                    str(self.config.path_extern_config):
                        {'bind': '/config', 'mode': 'rw'},
                    str(self.config.path_extern_ssl):
                        {'bind': '/ssl', 'mode': 'ro'},
                    str(self.config.path_extern_share):
                        {'bind': '/share', 'mode': 'rw'},
                })

            self.process_metadata()

            _LOGGER.info("Start docker addon %s with version %s",
                         self.image, self.version)

        except docker.errors.DockerException as err:
            _LOGGER.error("Can't run %s -> %s", self.image, err)
            return False

        return True

    async def update(self, tag):
        """Update homeassistant docker image."""
        if self._lock.locked():
            _LOGGER.error("Can't excute update while a task is in progress")
            return False

        async with self._lock:
            if await self.loop.run_in_executor(None, self._update, tag):
                await self.loop.run_in_executor(None, self._run)
                return True

            return False
