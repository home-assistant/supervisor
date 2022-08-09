"""Evaluation class for CGroup version."""
import logging

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

CGROUP_V1_VERSION = "1"
CGROUP_V2_VERSION = "2"

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateCGroupVersion(coresys)


class EvaluateCGroupVersion(EvaluateBase):
    """Evaluate Docker configuration."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CGROUP_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "The CGroup version used by Docker is not supported"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self):
        """Run evaluation."""
        cgroup_version = self.sys_docker.info.cgroup

        expected_version = [CGROUP_V1_VERSION]
        if self.coresys.os.available:
            expected_version.append(CGROUP_V2_VERSION)

        if cgroup_version not in expected_version:
            _LOGGER.warning(
                "Docker cgroup version %s is not supported! %s",
                cgroup_version,
                expected_version,
            )
            return True

        return False
