"""Helpers to check core security."""
from typing import List, Optional

from ...const import CoreState
from ..const import ContextType, IssueType
from .base import CheckBase


class CheckCoreSecurity(CheckBase):
    """CheckCoreSecurity class for check."""

    async def run_check(self) -> None:
        """Run check if not affected by issue."""
        for addon in self.sys_addons.installed:
            if not addon.pwned:
                continue

    async def approve_check(self, reference: Optional[str] = None) -> bool:
        """Approve check if it is affected by issue."""

    @property
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.PWNED

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.ADDON

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return [CoreState.RUNNING]
