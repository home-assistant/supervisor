"""Helpers to evaluate the system."""
import logging
from typing import List, Set

from ..coresys import CoreSys, CoreSysAttributes
from .const import UnhealthyReason, UnsupportedReason
from .evaluations.base import EvaluateBase
from .evaluations.container import EvaluateContainer
from .evaluations.dbus import EvaluateDbus
from .evaluations.docker_configuration import EvaluateDockerConfiguration
from .evaluations.docker_version import EvaluateDockerVersion
from .evaluations.job_conditions import EvaluateJobConditions
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

        self.cached_images: Set[str] = set()

        self._container = EvaluateContainer(coresys)
        self._dbus = EvaluateDbus(coresys)
        self._docker_configuration = EvaluateDockerConfiguration(coresys)
        self._docker_version = EvaluateDockerVersion(coresys)
        self._lxc = EvaluateLxc(coresys)
        self._network_manager = EvaluateNetworkManager(coresys)
        self._operating_system = EvaluateOperatingSystem(coresys)
        self._privileged = EvaluatePrivileged(coresys)
        self._systemd = EvaluateSystemd(coresys)
        self._job_conditions = EvaluateJobConditions(coresys)

    @property
    def all_evalutions(self) -> List[EvaluateBase]:
        """Return list of all evaluations."""
        return [
            self._container,
            self._dbus,
            self._docker_configuration,
            self._docker_version,
            self._lxc,
            self._network_manager,
            self._operating_system,
            self._privileged,
            self._systemd,
            self._job_conditions,
        ]

    async def evaluate_system(self) -> None:
        """Evaluate the system."""
        _LOGGER.info("Starting system evaluation with state %s", self.sys_core.state)

        for evaluation in self.all_evalutions:
            try:
                await evaluation()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning(
                    "Error during processing %s: %s", evaluation.reason, err
                )
                self.sys_capture_exception(err)

        if any(reason in self.sys_resolution.unsupported for reason in UNHEALTHY):
            self.sys_resolution.unhealthy = UnhealthyReason.DOCKER

        _LOGGER.info("System evaluation complete")
