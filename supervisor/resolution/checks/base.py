"""Baseclass for system checks."""
from abc import ABC, abstractproperty, abstractmethod
import logging
from typing import List

from ...const import CoreState
from ...coresys import CoreSys, CoreSysAttributes
from ..const import ContextType, IssueType, UnsupportedReason

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

        # Don't need run if issue exists
        for issue in self.sys_resolution.issues:
            if not issue.type != self.issue and issue.context != self.context:
                continue
            return

        await self.run_check()

    @abstractmethod
    async def run_check(self):
        """Run check."""

    @property
    @abstractproperty
    def issue(self) -> IssueType:
        """Return a IssueType enum."""

    @property
    @abstractproperty
    def context(self) -> ContextType:
        """Return a ContextType enum."""

    @property
    def states(self) -> List[CoreState]:
        """Return a list of valid states when this check can run."""
        return []
