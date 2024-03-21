"""Evaluation class for virtualization image."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateVirtualizationImage(coresys)


class EvaluateVirtualizationImage(EvaluateBase):
    """Evaluate correct OS image used when running under virtualization."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.VIRTUALIZATION_IMAGE

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return "Image of Home Assistant OS in use does not support virtualization."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self):
        """Run evaluation."""
        if not self.sys_os.available:
            return False
        return self.sys_host.info.virtualization and self.sys_os.board not in {
            "ova",
            "generic-aarch64",
        }
