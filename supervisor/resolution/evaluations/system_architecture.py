"""Evaluation class for system architecture support."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateSystemArchitecture(coresys)


class EvaluateSystemArchitecture(EvaluateBase):
    """Evaluate if the current Supervisor architecture is supported."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SYSTEM_ARCHITECTURE

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return "System architecture is no longer supported. Move to a supported system architecture."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.INITIALIZE]

    async def evaluate(self):
        """Run evaluation."""
        return self.sys_host.info.sys_arch.supervisor in {
            "i386",
            "armhf",
            "armv7",
        }
