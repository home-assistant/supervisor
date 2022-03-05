"""Evaluation class for systemd-resolved."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateResolved(coresys)


class EvaluateResolved(EvaluateBase):
    """Evaluate systemd-resolved."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SYSTEMD_RESOLVED

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "Systemd-Resolved is required for DNS in Home Assistant."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self) -> bool:
        """Run evaluation."""
        return not self.sys_dbus.resolved.is_connected
