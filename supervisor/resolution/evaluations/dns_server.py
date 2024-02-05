"""Evaluation class for DNS server."""

from ...const import CoreState
from ...coresys import CoreSys
from ..const import ContextType, UnsupportedReason
from .base import EvaluateBase


def setup(coresys: CoreSys) -> EvaluateBase:
    """Initialize evaluation-setup function."""
    return EvaluateDNSServer(coresys)


class EvaluateDNSServer(EvaluateBase):
    """Evaluate job conditions."""

    @property
    def reason(self) -> UnsupportedReason:
        """Return a UnsupportedReason enum."""
        return UnsupportedReason.DNS_SERVER

    @property
    def on_failure(self) -> str:
        """Return a string that is printed when self.evaluate is True."""
        return "Found unsupported DNS server and fallback is disabled."

    @property
    def states(self) -> list[CoreState]:
        """Return a list of valid states when this evaluation can run."""
        return [CoreState.RUNNING]

    async def evaluate(self) -> None:
        """Run evaluation."""
        return (
            not self.sys_plugins.dns.fallback
            and len(
                [
                    issue
                    for issue in self.sys_resolution.issues
                    if issue.context == ContextType.DNS_SERVER
                ]
            )
            > 0
        )
