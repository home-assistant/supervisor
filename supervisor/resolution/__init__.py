"""Supervisor resolution center."""
import logging
from typing import List, Optional

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionError, ResolutionNotFound
from .const import (
    SCHEDULED_HEALTHCHECK,
    ContextType,
    IssueType,
    SuggestionType,
    UnsupportedReason,
)
from .data import Issue, Suggestion
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

        self._suggestions: List[Suggestion] = []
        self._issues: List[Issue] = []
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
    def issues(self) -> List[Issue]:
        """Return a list of issues."""
        return self._issues

    @issues.setter
    def issues(self, issue: Issue) -> None:
        """Add issues."""
        if issue not in self._issues:
            self._issues.append(issue)

    @property
    def suggestions(self) -> List[Suggestion]:
        """Return a list of suggestions that can handled."""
        return self._suggestions

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

    def get_suggestion(self, uuid: str) -> Suggestion:
        """Return suggestion with uuid."""
        for suggestion in self._suggestions:
            if suggestion.uuid != uuid:
                continue
            return suggestion
        raise ResolutionNotFound()

    def get_issue(self, uuid: str) -> Issue:
        """Return issue with uuid."""
        for issue in self._issues:
            if issue.uuid != uuid:
                continue
            return issue
        raise ResolutionNotFound()

    def create_issue(
        self,
        issue: IssueType,
        context: ContextType,
        reference: Optional[str] = None,
        suggestions: Optional[List[SuggestionType]] = None,
    ) -> None:
        """Create issues and suggestion."""
        self.issues = Issue(issue, context, reference)
        if not suggestions:
            return

        # Add suggestions
        for suggestion in suggestions:
            self.suggestions = Suggestion(suggestion, context, reference)

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
        if suggestion not in self._suggestions:
            _LOGGER.warning("Suggestion %s is not valid", suggestion.uuid)
            raise ResolutionError()

        if suggestion.type == SuggestionType.CLEAR_FULL_SNAPSHOT:
            self.storage.clean_full_snapshots()

        elif suggestion.type == SuggestionType.CREATE_FULL_SNAPSHOT:
            await self.sys_snapshots.do_snapshot_full()

        self._suggestions.remove(suggestion)
        await self.healthcheck()

    async def dismiss_suggestion(self, suggestion: Suggestion) -> None:
        """Dismiss suggested action."""
        if suggestion not in self._suggestions:
            _LOGGER.warning("The UUID %s is not valid suggestion", suggestion.uuid)
            raise ResolutionError()
        self._suggestions.remove(suggestion)

    async def dismiss_issue(self, issue: Issue) -> None:
        """Dismiss suggested action."""
        if issue not in self._issues:
            _LOGGER.warning("Issue %s is not valid", issue.uuid)
            raise ResolutionError()
        self._issues.remove(issue)
