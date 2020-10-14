"""Supervisor resolution center."""
from typing import List

from ..const import UnsupportedReason
from ..coresys import CoreSys, CoreSysAttributes
from .const import SCHEDULED_HEALTHCHECK, IssueType, Suggestions
from .free_space import check_free_space
from .notify import create_notifications


class ResolutionManager(CoreSysAttributes):
    """Resolution manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Resolution manager."""
        self.coresys: CoreSys = coresys
        self._suggestions: List[Suggestions] = []
        self._issues: List[IssueType] = []
        self._unsupported: List[UnsupportedReason] = []

    @property
    def issues(self) -> List[IssueType]:
        """Return a list of issues."""
        return self._issues

    @issues.setter
    def issues(self, issue: IssueType) -> None:
        """Add issues."""
        if issue not in self._issues:
            self._issues.append(issue)

    @property
    def suggestions(self) -> List[Suggestions]:
        """Return a list of suggestions that can handled."""
        return self._suggestions

    @suggestions.setter
    def suggestions(self, suggestion: Suggestions) -> None:
        """Add suggestion."""
        if suggestion not in self._suggestions:
            self._suggestions.append(suggestion)

    @property
    def unsupported(self) -> List[UnsupportedReason]:
        """Return a list of unsupported reasons."""
        return self._unsupported

    @unsupported.setter
    def unsupported(self, reason: UnsupportedReason) -> None:
        """Add a reason for unsupported."""
        if reason not in self._unsupported:
            self._unsupported.append(reason)

    def clear(self, collection: str) -> None:
        """Clear the contents of the collection."""
        if collection == "issues":
            self._issues = []
        elif collection == "suggestions":
            self._suggestions = []
        elif collection == "unsupported":
            self._unsupported = []

    async def load(self):
        """Load the resoulution manager."""
        # Initial healthcheck when the manager is loaded
        await self.healthcheck()

        # Schedule the healthcheck
        self.sys_scheduler.register_task(self.healthcheck, SCHEDULED_HEALTHCHECK)

    async def healthcheck(self):
        """Scheduled task to check for known issues."""
        # Check free space
        self.sys_run_in_executor(check_free_space, self.coresys)

        # Create notification for any known issues
        await create_notifications(self.coresys)
