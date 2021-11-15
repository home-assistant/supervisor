"""Evaluation class for privileged."""

from ...const import SupervisorState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluatePrivileged(coresys)


class EvaluatePrivileged(EvaluateBase):
    """Evaluate Privileged mode."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.PRIVILEGED

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "Supervisor does not run in Privileged mode."

    @property
    def states(self) -> list[SupervisorState]:
        """Return a list of valid states when this evaluation can run."""
        return [SupervisorState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        return not self.sys_supervisor.instance.privileged
