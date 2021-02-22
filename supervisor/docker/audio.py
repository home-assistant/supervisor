"""Audio docker object."""
import logging
from typing import Dict, List, Optional

import docker

from ..const import ENV_TIME, MACHINE_ID
from ..coresys import CoreSysAttributes
from ..docker.const import Capabilities
from ..hardware.const import PolicyGroup
from .interface import DockerInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)

AUDIO_DOCKER_NAME: str = "hassio_audio"


class DockerAudio(DockerInterface, CoreSysAttributes):
    """Docker Supervisor wrapper for Supervisor Audio."""

    @property
    def image(self) -> str:
        """Return name of Supervisor Audio image."""
        return self.sys_plugins.audio.image

    @property
    def name(self) -> str:
        """Return name of Docker container."""
        return AUDIO_DOCKER_NAME

    @property
    def volumes(self) -> Dict[str, Dict[str, str]]:
        """Return Volumes for the mount."""
        volumes = {
            "/dev": {"bind": "/dev", "mode": "ro"},
            str(self.sys_config.path_extern_audio): {"bind": "/data", "mode": "rw"},
            "/run/dbus": {"bind": "/run/dbus", "mode": "ro"},
            "/run/udev": {"bind": "/run/udev", "mode": "ro"},
        }

        # Machine ID
        if MACHINE_ID.exists():
            volumes.update({str(MACHINE_ID): {"bind": str(MACHINE_ID), "mode": "ro"}})

        return volumes

    @property
    def cgroups_rules(self) -> List[str]:
        """Return a list of needed cgroups permission."""
        return self.sys_hardware.policy.get_cgroups_rules(
            PolicyGroup.AUDIO
        ) + self.sys_hardware.policy.get_cgroups_rules(PolicyGroup.BLUETOOTH)

    @property
    def capabilities(self) -> List[str]:
        """Generate needed capabilities."""
        return [cap.value for cap in (Capabilities.SYS_NICE, Capabilities.SYS_RESOURCE)]

    @property
    def ulimits(self) -> List[docker.types.Ulimit]:
        """Generate ulimits for audio."""
        if not self.sys_docker.info.support_cpu_realtime:
            return None
        return [docker.types.Ulimit(name="rtprio", soft=99)]

    @property
    def cpu_rt_runtime(self) -> Optional[int]:
        """Limit CPU real-time runtime in microseconds."""
        if not self.sys_docker.info.support_cpu_realtime:
            return None
        return 950000

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
            tag=str(self.sys_plugins.audio.version),
            init=False,
            ipv4=self.sys_docker.network.audio,
            name=self.name,
            hostname=self.name.replace("_", "-"),
            detach=True,
            cap_add=self.capabilities,
            ulimits=self.ulimits,
            cpu_rt_runtime=self.cpu_rt_runtime,
            device_cgroup_rules=self.cgroups_rules,
            environment={ENV_TIME: self.sys_config.timezone},
            volumes=self.volumes,
        )

        self._meta = docker_container.attrs
        _LOGGER.info(
            "Starting Audio %s with version %s - %s",
            self.image,
            self.version,
            self.sys_docker.network.audio,
        )
