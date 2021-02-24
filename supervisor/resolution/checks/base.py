"""Baseclass for system checks."""
from abc import ABC, abstractmethod, abstractproperty
import logging
from typing import List, Optional

from ...const import CoreState
from ...coresys import CoreSys, CoreSysAttributes
from ..const import ContextType, IssueType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class CheckBase(ABC, CoreSysAttributes):
    """Baseclass for check."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        self.coresys = coresys

    async def __call__(self) -> None:
        """Execute the evaluation."""
        if self.sys_core.state not in self.states:
            return

        # Check if system is affected by the issue
        affected: bool = False
        for issue in self.sys_resolution.issues:
            if issue.type != self.issue or issue.context != self.context:
                continue
            affected = True

            # Check if issue still exists
            _LOGGER.debug(
                "Run approve check for %s/%s - %s",
                self.issue,
                self.context,
                issue.reference,
            )
            if await self.approve_check(reference=issue.reference):
                continue
            self.sys_resolution.dismiss_issue(issue)

        # System is not affected
        if affected and not self.multible:
            return
        _LOGGER.info("Run check for %s/%s", self.issue, self.context)
        await self.run_check()

    @abstractmethod
    async def run_check(self) -> None:
        """Run check if not affected by issue."""

    @abstractmethod
    async def approve_check(self, reference: Optional[str] = None) -> bool:
        """Approve check if it is affected by issue."""

    @property
    @abstractproperty
    def issue(self) -> IssueType:
        """Return a IssueType enum."""

    @property
    @abstractproperty
    def context(self) -> ContextType:
        """Return a ContextType enum."""

    @property
    def multible(self) -> bool:
        """Return True if they can have multible issues referenced by reference."""
        return self.context in (ContextType.ADDON, ContextType.PLUGIN)

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return []
