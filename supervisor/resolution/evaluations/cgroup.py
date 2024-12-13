"""Evaluation class for CGroup version."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import CGROUP_V1_VERSION, CGROUP_V2_VERSION, UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateCGroupVersion(coresys)


class EvaluateCGroupVersion(EvaluateBase):
    """Evaluate Docker configuration."""

    @property
    def expected_versions(self) -> set[str]:
        """Return expected cgroup versions."""
        return {CGROUP_V1_VERSION, CGROUP_V2_VERSION}

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CGROUP_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return f"Docker cgroup version {self.sys_docker.info.cgroup} is not supported! {self.expected_versions}"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        return self.sys_docker.info.cgroup not in self.expected_versions
