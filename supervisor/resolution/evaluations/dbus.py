"""Evaluation class for dbus."""
from typing import List

from ...const import SOCKET_DBUS, CoreState
from ..const import UnsupportedReason
from .base import EvaluateBase


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
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self) -> None:
        """Run evaluation."""
        return not SOCKET_DBUS.exists()
