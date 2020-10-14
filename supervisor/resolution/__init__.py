"""Supervisor resolution center."""
import logging
from typing import List

from ..coresys import CoreSys, CoreSysAttributes
from ..resolution.const import UnsupportedReason
from .const import SCHEDULED_HEALTHCHECK, IssueType, Suggestion
from .free_space import ResolutionStorage
from .notify import ResolutionNotify

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionManager(CoreSysAttributes):
    """Resolution manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Resolution manager."""
        self.coresys: CoreSys = coresys
        self._notify = ResolutionNotify(coresys)
        self._storage = ResolutionStorage(coresys)
        self._dismissed_suggestions: List[Suggestion] = []
        self._suggestions: List[Suggestion] = []
        self._issues: List[IssueType] = []
        self._unsupported: List[UnsupportedReason] = []

    @property
    def storage(self) -> ResolutionStorage:
        """Return the ResolutionStorage class."""
        return self._storage

    @property
    def notify(self) -> ResolutionNotify:
        """Return the ResolutionNotify class."""
        return self._notify

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
    def suggestions(self) -> List[Suggestion]:
        """Return a list of suggestions that can handled."""
        return [x for x in self._suggestions if x not in self._dismissed_suggestions]

    @suggestions.setter
    def suggestions(self, suggestion: Suggestion) -> None:
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

    async def load(self):
        """Load the resoulution manager."""
        # Initial healthcheck when the manager is loaded
        await self.healthcheck()

        # Schedule the healthcheck
        self.sys_scheduler.register_task(self.healthcheck, SCHEDULED_HEALTHCHECK)

    async def healthcheck(self):
        """Scheduled task to check for known issues."""
        # Check free space
        self.sys_run_in_executor(self.storage.check_free_space)

        # Create notification for any known issues
        await self.notify.issue_notifications()

    async def apply_suggestion(self, suggestion: Suggestion) -> None:
        """Apply suggested action."""
        if suggestion not in self.suggestions:
            _LOGGER.warning("Suggestion %s is not valid", suggestion)
            return

        if suggestion == Suggestion.CLEAR_FULL_SNAPSHOT:
            self.storage.clean_full_snapshots()

        elif suggestion == Suggestion.CREATE_FULL_SNAPSHOT:
            await self.sys_snapshots.do_snapshot_full()

        self._suggestions.remove(suggestion)
        await self.healthcheck()

    async def dismiss_suggestion(self, suggestion: Suggestion) -> None:
        """Dismiss suggested action."""
        if suggestion not in self.suggestions:
            _LOGGER.warning("Suggestion %s is not valid", suggestion)
            return

        if suggestion not in self._dismissed_suggestions:
            self._dismissed_suggestions.append(suggestion)
