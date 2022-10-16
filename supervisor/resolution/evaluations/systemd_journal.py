"""Evaluation class for systemd journal."""

from ...const import CoreState
from ...coresys import CoreSys
from ...host.const import HostFeature
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateSystemdJournal(coresys)


class EvaluateSystemdJournal(EvaluateBase):
    """Evaluate systemd journal."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SYSTEMD_JOURNAL

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return "Systemd journal is not working correctly or inaccessible"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self) -> bool:
        """Run evaluation, return true if system fails."""
        return HostFeature.JOURNAL not in self.sys_host.features
