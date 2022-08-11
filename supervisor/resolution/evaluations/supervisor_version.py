"""Evaluation class for supervisor version."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateSupervisorVersion(coresys)


class EvaluateSupervisorVersion(EvaluateBase):
    """Evaluate supervisor version."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SUPERVISOR_VERSION

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "Not using latest version of Supervisor and auto update is disabled."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        return not self.sys_updater.auto_update and self.sys_supervisor.need_update
