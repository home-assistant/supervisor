"""Init file for HassIO docker object."""
import asyncio

import docker

import . from DockerBase


class DockerHomeAssistant(DockerBase):
    """Docker hassio wrapper for HomeAssistant."""

    def _run():
        """Run docker image.

        Need run inside executor.
        """
        try:
            self.container = self.dock.containers.run(
                self.image,
                remove=True,
                network_mode='host',
                restart_policy={
                    "Name": "always",
                    "MaximumRetryCount": 10,
                },
                volumes={
                    '/data': {'bind': '/data', 'mode': 'rw'}
                })
        except docker.errors.APIError as err:
            _LOGGER.error("Can't run %s", self.image)
            return False

        return True
