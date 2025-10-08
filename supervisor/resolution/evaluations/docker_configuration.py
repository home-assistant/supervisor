"""Evaluation class for docker configuration."""

import logging

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

EXPECTED_LOGGING = "journald"
EXPECTED_STORAGE = ("overlay2", "overlayfs")

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
        """Return a string that is printed when self.evaluate is True."""
        return "The configuration of Docker is not supported"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        storage_driver = self.sys_docker.info.storage
        logging_driver = self.sys_docker.info.logging

        is_unsupported = False

        if storage_driver not in EXPECTED_STORAGE:
            is_unsupported = True
            _LOGGER.warning(
                "Docker storage driver %s is not supported!", storage_driver
            )

        if logging_driver != EXPECTED_LOGGING:
            is_unsupported = True
            _LOGGER.warning(
                "Docker logging driver %s is not supported!", logging_driver
            )

        return is_unsupported
