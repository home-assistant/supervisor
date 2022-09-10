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

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the evaluation class."""
        super().__init__(coresys)
        self.coresys = coresys

        self._expected_versions = {CGROUP_V1_VERSION}
        if self.coresys.os.available:
            self._expected_versions.add(CGROUP_V2_VERSION)

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CGROUP_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Docker cgroup version {self.sys_docker.info.cgroup} is not supported! {self._expected_versions}"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        return self.sys_docker.info.cgroup not in self._expected_versions
