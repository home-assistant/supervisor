"""Helpers to evaluate the system."""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from .const import UnhealthyReason, UnsupportedReason
from .evaluations.container import EvaluateContainer
from .evaluations.dbus import EvaluateDbus
from .evaluations.docker_configuration import EvaluateDockerConfiguration
from .evaluations.docker_version import EvaluateDockerVersion
from .evaluations.lxc import EvaluateLxc
from .evaluations.network_manager import EvaluateNetworkManager
from .evaluations.operating_system import EvaluateOperatingSystem
from .evaluations.privileged import EvaluatePrivileged
from .evaluations.systemd import EvaluateSystemd

_LOGGER: logging.Logger = logging.getLogger(__name__)

UNHEALTHY = [
    UnsupportedReason.CONTAINER,
    UnsupportedReason.DOCKER_VERSION,
    UnsupportedReason.LXC,
    UnsupportedReason.PRIVILEGED,
]


class ResolutionEvaluation(CoreSysAttributes):
    """Evaluation class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        self.coresys = coresys

        self._container = EvaluateContainer(coresys)
        self._dbus = EvaluateDbus(coresys)
        self._docker_configuration = EvaluateDockerConfiguration(coresys)
        self._docker_version = EvaluateDockerVersion(coresys)
        self._lxc = EvaluateLxc(coresys)
        self._network_manager = EvaluateNetworkManager(coresys)
        self._operating_system = EvaluateOperatingSystem(coresys)
        self._privileged = EvaluatePrivileged(coresys)
        self._systemd = EvaluateSystemd(coresys)

    async def evaluate_system(self) -> None:
        """Evaluate the system."""
        _LOGGER.info("Starting system evaluation with state %s", self.sys_core.state)
        await self._container()
        await self._dbus()
        await self._docker_configuration()
        await self._docker_version()
        await self._lxc()
        await self._network_manager()
        await self._operating_system()
        await self._privileged()
        await self._systemd()

        if any(reason in self.sys_resolution.unsupported for reason in UNHEALTHY):
            self.sys_resolution.unhealthy = UnhealthyReason.DOCKER

        _LOGGER.info("System evaluation complete")
