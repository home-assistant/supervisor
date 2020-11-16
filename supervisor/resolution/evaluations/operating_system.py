"""Evaluation class for operating system."""
from typing import List

from ...const import CoreState
from ..const import UnsupportedReason
from .base import EvaluateBase

SUPPORTED_OS = ["Debian GNU/Linux 10 (buster)"]


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
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self):
        """Run evaluation."""
        if self.sys_os.available:
            return False
        return self.sys_host.info.operating_system not in SUPPORTED_OS
