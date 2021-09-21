"""Evaluation class for Content Trust."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateContentTrust(coresys)


class EvaluateContentTrust(EvaluateBase):
    """Evaluate system content trust level."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.CONTENT_TRUST

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "System run with disabled trusted content security."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE, CoreState.SETUP, CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        return not self.sys_security.content_trust
