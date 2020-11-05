"""Evaluation class for docker configuration."""
import logging
from typing import List

from ...const import CoreState
from ..const import UnsupportedReason
from .base import EvaluateBase

EXPECTED_LOGGING = "journald"
EXPECTED_STORAGE = "overlay2"

_LOGGER: logging.Logger = logging.getLogger(__name__)


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
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        _storage = self.sys_docker.info.storage
        _logging = self.sys_docker.info.logging

        if _storage != EXPECTED_STORAGE:
            _LOGGER.warning("Docker storage driver %s is not supported!", _storage)

        if _logging != EXPECTED_LOGGING:
            _LOGGER.warning("Docker logging driver %s is not supported!", _logging)

        return _storage != EXPECTED_STORAGE or _logging != EXPECTED_LOGGING
