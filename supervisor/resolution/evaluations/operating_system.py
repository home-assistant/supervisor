"""Evaluation class for operating system."""

from ...const import SupervisorState
from ...coresys import CoreSys
from ..const import UnsupportedReason
from .base import EvaluateBase

SUPPORTED_OS = ["Debian GNU/Linux 10 (buster)", "Debian GNU/Linux 11 (bullseye)"]


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateOperatingSystem(coresys)


class EvaluateOperatingSystem(EvaluateBase):
    """Evaluate the operating system."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.OS

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is False."""
        return f"Detected unsupported OS: {self.sys_host.info.operating_system}"

    @property
    def states(self) -> list[SupervisorState]:
        """Return a list of valid states when this evaluation can run."""
        return [SupervisorState.SETUP]

    async def evaluate(self):
        """Run evaluation."""
        if self.sys_os.available:
            return False
        return self.sys_host.info.operating_system not in SUPPORTED_OS
