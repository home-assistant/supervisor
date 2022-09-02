"""Evaluation class for connectivity check."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateConnectivityCheck(coresys)


class EvaluateConnectivityCheck(EvaluateBase):
    """Evaluate connectivity check."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CONNECTIVITY_CHECK

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when system fails this evaluation."""
        return "Connectivity checks are required for Home Assistant."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    async def evaluate(self) -> bool:
        """Run evaluation, return true if system fails."""
        return self.sys_dbus.network.connectivity_enabled is False
