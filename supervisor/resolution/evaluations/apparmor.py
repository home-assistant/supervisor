"""Evaluation class for dbus."""
from pathlib import Path
from typing import List

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

_APPARMOR_KERNEL = Path("/sys/module/apparmor/parameters/enabled")


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateAppArmor(coresys)


class EvaluateAppArmor(EvaluateBase):
    """Evaluate is supported/enabled AppArmor."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.APPARMOR

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "AppArmor is required for Home Assistant."

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self) -> None:
        """Run evaluation."""
        try:
            return _APPARMOR_KERNEL.read_text().strip().upper() != "Y"
        except OSError:
            return True
