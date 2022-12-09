"""Evaluation class for systemd."""

from ...const import CoreState
from ...coresys import CoreSys
from ...host.const import HostFeature
from ..const import UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateSystemd(coresys)


class EvaluateSystemd(EvaluateBase):
    """Evaluate systemd."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.SYSTEMD

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return "Systemd is not correctly working"

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.SETUP]

    async def evaluate(self):
        """Run evaluation."""
        return any(
            feature not in self.sys_host.features
            for feature in (
                HostFeature.HOSTNAME,
                HostFeature.SERVICES,
                HostFeature.SHUTDOWN,
                HostFeature.REBOOT,
                HostFeature.TIMEDATE,
            )
        )
