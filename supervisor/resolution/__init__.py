"""Supervisor resolution center."""
from datetime import time
import logging
from typing import List, Optional

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionError, ResolutionNotFound
from .check import ResolutionCheck
from .const import (
    SCHEDULED_HEALTHCHECK,
    ContextType,
    IssueType,
    SuggestionType,
    UnhealthyReason,
    UnsupportedReason,
)
from .data import Issue, Suggestion
from .evaluate import ResolutionEvaluation
from .fixup import ResolutionFixup
from .notify import ResolutionNotify

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionManager(CoreSysAttributes):
    """Resolution manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Resolution manager."""
        self.coresys: CoreSys = coresys
        self._evaluate = ResolutionEvaluation(coresys)
        self._check = ResolutionCheck(coresys)
        self._fixup = ResolutionFixup(coresys)
        self._notify = ResolutionNotify(coresys)

        self._suggestions: List[Suggestion] = []
        self._issues: List[Issue] = []
        self._unsupported: List[UnsupportedReason] = []
        self._unhealthy: List[UnhealthyReason] = []

    @property
    def evaluate(self) -> ResolutionEvaluation:
        """Return the ResolutionEvaluation class."""
        return self._evaluate

    @property
    def check(self) -> ResolutionCheck:
        """Return the ResolutionCheck class."""
        return self._check

    @property
    def fixup(self) -> ResolutionFixup:
        """Return the ResolutionFixup class."""
        return self._fixup

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

    @property
    def unhealthy(self) -> List[UnhealthyReason]:
        """Return a list of unsupported reasons."""
        return self._unhealthy

    @unhealthy.setter
    def unhealthy(self, reason: UnhealthyReason) -> None:
        """Add a reason for unsupported."""
        if reason not in self._unhealthy:
            self._unhealthy.append(reason)

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
        self.sys_scheduler.register_task(self.fixup.run_autofix, time(hour=2))

    async def healthcheck(self):
        """Scheduled task to check for known issues."""
        await self.check.check_system()

        # Create notification for any known issues
        await self.notify.issue_notifications()

    async def apply_suggestion(self, suggestion: Suggestion) -> None:
        """Apply suggested action."""
        if suggestion not in self._suggestions:
            _LOGGER.warning("Suggestion %s is not valid", suggestion.uuid)
            raise ResolutionError()

        await self.fixup.apply_fixup(suggestion)
        await self.healthcheck()

    def dismiss_suggestion(self, suggestion: Suggestion) -> None:
        """Dismiss suggested action."""
        if suggestion not in self._suggestions:
            _LOGGER.warning("The UUID %s is not valid suggestion", suggestion.uuid)
            raise ResolutionError()
        self._suggestions.remove(suggestion)

    def dismiss_issue(self, issue: Issue) -> None:
        """Dismiss suggested action."""
        if issue not in self._issues:
            _LOGGER.warning("The UUID %s is not a valid issue", issue.uuid)
            raise ResolutionError()
        self._issues.remove(issue)

    def dismiss_unsupported(self, reason: Issue) -> None:
        """Dismiss a reason for unsupported."""
        if reason not in self._unsupported:
            _LOGGER.warning("The reason %s is not active", reason)
            raise ResolutionError()
        self._unsupported.remove(reason)
