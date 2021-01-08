"""Evaluation class for lxc."""
from typing import List

from ...const import CoreState
from ..const import UnsupportedReason
from .base import EvaluateBase


class EvaluateLxc(EvaluateBase):
    """Evaluate if running inside LXC."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.LXC

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return "Detected Docker running inside LXC."

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        return self.sys_docker.info.inside_lxc
