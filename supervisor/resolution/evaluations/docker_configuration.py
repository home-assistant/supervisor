"""Evaluation class for docker configuration."""
import logging

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

EXPECTED_LOGGING = "journald"
EXPECTED_STORAGE = "overlay2"
CGROUP_V1_VERSION = "1"
CGROUP_V2_VERSION = "2"

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateDockerConfiguration(coresys)


class EvaluateDockerConfiguration(EvaluateBase):
    """Evaluate Docker configuration."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.DOCKER_CONFIGURATION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "The configuration of Docker is not supported"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        storage_driver = self.sys_docker.info.storage
        logging_driver = self.sys_docker.info.logging
        cgroup_version = self.sys_docker.info.cgroup

        if storage_driver != EXPECTED_STORAGE:
            _LOGGER.warning(
                "Docker storage driver %s is not supported!", storage_driver
            )

        if logging_driver != EXPECTED_LOGGING:
            _LOGGER.warning(
                "Docker logging driver %s is not supported!", logging_driver
            )

        expected_version = [CGROUP_V1_VERSION]
        if self.coresys.os.available:
            expected_version.append(CGROUP_V2_VERSION)

        if cgroup_version not in expected_version:
            _LOGGER.warning(
                "Docker cgroup version %s is not supported!", cgroup_version
            )

        return (
            storage_driver != EXPECTED_STORAGE
            or logging_driver != EXPECTED_LOGGING
            or cgroup_version not in CGROUP_V2_VERSION
        )
