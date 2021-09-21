"""Evaluation class for network manager."""

from ...const import CoreState
from ...coresys import CoreSys
from ...host.const import HostFeature
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateNetworkManager(coresys)


class EvaluateNetworkManager(EvaluateBase):
    """Evaluate network manager."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.NETWORK_MANAGER

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "NetworkManager is not correctly configured"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP, CoreState.RUNNING]

    async def evaluate(self):
        """Run evaluation."""
        return HostFeature.NETWORK not in self.sys_host.features
