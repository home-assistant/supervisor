"""Supervisor resolution center."""
import logging
from typing import Any, Optional

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionError, ResolutionNotFound
from ..utils.common import FileConfiguration
from .check import ResolutionCheck
from .const import (
    FILE_CONFIG_RESOLUTION,
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
from .validate import SCHEMA_RESOLUTION_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionManager(FileConfiguration, CoreSysAttributes):
    """Resolution manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Resolution manager."""
        super().__init__(FILE_CONFIG_RESOLUTION, SCHEMA_RESOLUTION_CONFIG)

        self.coresys: CoreSys = coresys
        self._evaluate = ResolutionEvaluation(coresys)
        self._check = ResolutionCheck(coresys)
        self._fixup = ResolutionFixup(coresys)
        self._notify = ResolutionNotify(coresys)

        self._suggestions: list[Suggestion] = []
        self._issues: list[Issue] = []
        self._unsupported: list[UnsupportedReason] = []
        self._unhealthy: list[UnhealthyReason] = []

    @property
    def data(self) -> dict[str, Any]:
        """Return data."""
        return self._data

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
    def issues(self) -> list[Issue]:
        """Return a list of issues."""
        return self._issues

    @issues.setter
    def issues(self, issue: Issue) -> None:
        """Add issues."""
        if issue in self._issues:
            return
        _LOGGER.info(
            "Create new issue %s - %s / %s", issue.type, issue.context, issue.reference
        )
        self._issues.append(issue)

    @property
    def suggestions(self) -> list[Suggestion]:
        """Return a list of suggestions that can handled."""
        return self._suggestions

    @suggestions.setter
    def suggestions(self, suggestion: Suggestion) -> None:
        """Add suggestion."""
        if suggestion in self._suggestions:
            return
        _LOGGER.info(
            "Create new suggestion %s - %s / %s",
            suggestion.type,
            suggestion.context,
            suggestion.reference,
        )
        self._suggestions.append(suggestion)

    @property
    def unsupported(self) -> list[UnsupportedReason]:
        """Return a list of unsupported reasons."""
        return self._unsupported

    @unsupported.setter
    def unsupported(self, reason: UnsupportedReason) -> None:
        """Add a reason for unsupported."""
        if reason not in self._unsupported:
            self._unsupported.append(reason)

    @property
    def unhealthy(self) -> list[UnhealthyReason]:
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
        suggestions: Optional[list[SuggestionType]] = None,
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
        await self.check.check_system()
        await self.evaluate.evaluate_system()

        # Run autofix if possible
        await self.fixup.run_autofix()

        # Create notification for any known issues
        await self.notify.issue_notifications()

    async def apply_suggestion(self, suggestion: Suggestion) -> None:
        """Apply suggested action."""
        if suggestion not in self._suggestions:
            raise ResolutionError(
                f"Suggestion {suggestion.uuid} is not valid", _LOGGER.warning
            )

        await self.fixup.apply_fixup(suggestion)
        await self.healthcheck()

    def dismiss_suggestion(self, suggestion: Suggestion) -> None:
        """Dismiss suggested action."""
        if suggestion not in self._suggestions:
            raise ResolutionError(
                f"The UUID {suggestion.uuid} is not valid suggestion", _LOGGER.warning
            )
        self._suggestions.remove(suggestion)

    def dismiss_issue(self, issue: Issue) -> None:
        """Dismiss suggested action."""
        if issue not in self._issues:
            raise ResolutionError(
                f"The UUID {issue.uuid} is not a valid issue", _LOGGER.warning
            )
        self._issues.remove(issue)

    def dismiss_unsupported(self, reason: Issue) -> None:
        """Dismiss a reason for unsupported."""
        if reason not in self._unsupported:
            raise ResolutionError(f"The reason {reason} is not active", _LOGGER.warning)
        self._unsupported.remove(reason)
