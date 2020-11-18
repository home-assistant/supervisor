"""Evaluation class for network manager."""
from typing import List

from ...const import CoreState, HostFeature
from ..const import UnsupportedReason
from .base import EvaluateBase


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
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP, CoreState.RUNNING]

    async def evaluate(self):
        """Run evaluation."""
        return HostFeature.NETWORK not in self.sys_host.features
