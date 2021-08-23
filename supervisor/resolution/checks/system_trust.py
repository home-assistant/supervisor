"""Helpers to check system trust."""
from enum import Enum
import logging
from typing import List, Optional

from ...const import CoreState
from ...coresys import CoreSys
from ...exceptions import CodeNotaryError, CodeNotaryUntrusted
from ..const import ContextType, IssueType, UnhealthyReason
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class TrustReference(str, Enum):
    """List of trust & reference."""

    CORE = "core"
    SUPERVISOR = "supervisor"


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckSystemTrust(coresys)


class CheckSystemTrust(CheckBase):
    """CheckSystemTrust class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self.sys_security.content_trust:
            _LOGGER.warning(
                "Skipping %s, content_trust is globally disabled", self.slug
            )
            return

        # Supervisor
        try:
            await self.sys_supervisor.check_trust()
        except CodeNotaryUntrusted:
            self.sys_resolution.unhealthy = UnhealthyReason.UNTRUSTED
            self.sys_resolution.create_issue(
                IssueType.TRUST,
                ContextType.SYSTEM,
                reference=TrustReference.SUPERVISOR.value,
            )
        except CodeNotaryError:
            pass

        # Core
        try:
            await self.sys_homeassistant.core.check_trust()
        except CodeNotaryUntrusted:
            self.sys_resolution.unhealthy = UnhealthyReason.UNTRUSTED
            self.sys_resolution.create_issue(
                IssueType.TRUST,
                ContextType.SYSTEM,
                reference=TrustReference.CORE.value,
            )
        except CodeNotaryError:
            pass

    async def approve_check(self, reference: Optional[str] = None) -> bool:
        """Approve check if it is affected by issue."""
        if reference == TrustReference.SUPERVISOR:
            try:
                await self.sys_supervisor.check_trust()
            except CodeNotaryError:
                return True

        if reference == TrustReference.CORE:
            try:
                await self.sys_homeassistant.core.check_trust()
            except CodeNotaryError:
                return True

        return False

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.TRUST

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
