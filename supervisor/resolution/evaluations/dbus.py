"""Evaluation class for dbus."""

from ...const import SOCKET_DBUS, CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateDbus(coresys)


class EvaluateDbus(EvaluateBase):
    """Evaluate dbus."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.DBUS

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "D-Bus is required for Home Assistant."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self) -> None:
        """Run evaluation."""
        return not SOCKET_DBUS.exists()
