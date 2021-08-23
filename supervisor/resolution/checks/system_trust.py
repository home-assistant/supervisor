"""Helpers to check supervisor security."""
from enum import Enum
import logging
from typing import List, Optional

from ...const import CoreState
from ...coresys import CoreSys
from ...exceptions import CodeNotaryUntrusted
from ..const import ContextType, IssueType, UnhealthyReason
from .base import CheckBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class TrustReference(str, Enum):
    """List of trust & reference."""

    CORE = "core"
    SUPERVISOR = "supervisor"


def setup(coresys: CoreSys) -> CheckBase:
    """Check setup function."""
    return CheckSupervisorSecurity(coresys)


class CheckSupervisorSecurity(CheckBase):
    """CheckSupervisorSecurity class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        if not self.sys_security.content_trust:
            _LOGGER.warning(
                "Skipping %s, content_trust is globally disabled", self.slug
            )
            return

        # Supervisor
        try:
            await self.sys_supervisor.instance.check_trust()
        except CodeNotaryUntrusted:
            self.sys_resolution.unhealthy = UnhealthyReason.UNTRUSTED
            self.sys_resolution.create_issue(
                IssueType.TRUST,
                ContextType.SYSTEM,
                reference=TrustReference.SUPERVISOR.value,
            )

        # Core
        try:
            await self.sys_homeassistant.core.instance.check_trust()
        except CodeNotaryUntrusted:
            self.sys_resolution.unhealthy = UnhealthyReason.UNTRUSTED
            self.sys_resolution.create_issue(
                IssueType.TRUST,
                ContextType.SYSTEM,
                reference=TrustReference.SUPERVISOR.value,
            )

    async def approve_check(self, reference: Optional[str] = None) -> bool:
        """Approve check if it is affected by issue."""
        if reference == TrustReference.SUPERVISOR:
            try:
                await self.sys_supervisor.instance.check_trust()
            except CodeNotaryUntrusted:
                return False

        if reference == TrustReference.CORE:
            try:
                await self.sys_homeassistant.core.instance.check_trust()
            except CodeNotaryUntrusted:
                return False

        return True

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
