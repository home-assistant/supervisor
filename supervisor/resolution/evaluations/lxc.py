"""Evaluation class for lxc."""
from contextlib import suppress
from pathlib import Path

from ...const import SupervisorState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateLxc(coresys)


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
    def states(self) -> list[SupervisorState]:
        """Return a list of valid states when this evaluation can run."""
        return [SupervisorState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        with suppress(OSError):
            if "container=lxc" in Path("/proc/1/environ").read_text(encoding="utf-8"):
                return True
        return Path("/dev/lxd/sock").exists()
