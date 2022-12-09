"""Evaluation class for Job Conditions."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateJobConditions(coresys)


class EvaluateJobConditions(EvaluateBase):
    """Evaluate job conditions."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.JOB_CONDITIONS

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return "Found unsupported job conditions settings."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE, CoreState.SETUP, CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        return len(self.sys_jobs.ignore_conditions) > 0
