"""Audio docker object."""
from contextlib import suppress
import logging
from pathlib import Path
from typing import Dict

from ..const import ENV_TIME
from ..coresys import CoreSysAttributes
from ..exceptions import DockerAPIError
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

AUDIO_DOCKER_NAME: str = "hassio_audio"


class DockerAudio(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for Supervisor Audio."""

    @property
    def image(self) -> str:
        """Return name of Supervisor Audio image."""
        return self.sys_audio.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return AUDIO_DOCKER_NAME

    @property
    def volumes(self) -> Dict[str, Dict[str, str]]:
        """Return Volumes for the mount."""
        volumes = {
            str(self.sys_config.path_extern_audio): {"bind": "/data", "mode": "rw"},
            "/run/dbus": {"bind": "/run/dbus", "mode": "ro"},
        }

        # SND support
        if Path("/dev/snd").exists():
            volumes.update({"/dev/snd": {"bind": "/dev/snd", "mode": "rw"}})
        else:
            _LOGGER.warning("Kernel have no audio support in")

        return volumes

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
            version=self.sys_audio.version,
            init=False,
            ipv4=self.sys_docker.network.audio,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            privileged=True,
            environment={ENV_TIME: self.sys_timezone},
            volumes=self.volumes,
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Start Audio %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.audio,
        )
