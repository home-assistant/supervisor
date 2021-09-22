"""Evaluation class for host agent."""

from ...const import CoreState
from ...coresys import CoreSys
from ...host.const import HostFeature
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateOSAgent(coresys)


class EvaluateOSAgent(EvaluateBase):
    """Evaluate host agent support."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.OS_AGENT

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "OS-Agent is not correctly working"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self):
        """Run evaluation."""
        return HostFeature.OS_AGENT not in self.sys_host.features
