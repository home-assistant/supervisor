"""Evaluation class for docker configuration."""
import logging

from ...const import SupervisorState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

EXPECTED_LOGGING = "journald"
EXPECTED_STORAGE = "overlay2"

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
    def states(self) -> list[SupervisorState]:
        """Return a list of valid states when this evaluation can run."""
        return [SupervisorState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        _storage = self.sys_docker.info.storage
        _logging = self.sys_docker.info.logging

        if _storage != EXPECTED_STORAGE:
            _LOGGER.warning("Docker storage driver %s is not supported!", _storage)

        if _logging != EXPECTED_LOGGING:
            _LOGGER.warning("Docker logging driver %s is not supported!", _logging)

        return _storage != EXPECTED_STORAGE or _logging != EXPECTED_LOGGING
