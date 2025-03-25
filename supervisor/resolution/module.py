"""Supervisor resolution center."""

import logging
from typing import Any

import attr

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionError, ResolutionNotFound
from ..homeassistant.const import WSEvent
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
from .data import HealthChanged, Issue, Suggestion, SupportedChanged
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

    async def load_modules(self):
        """Load resolution evaluation, check and fixup modules."""

        def _load_modules():
            """Load and setup all resolution modules."""
            self._evaluate.load_modules()
            self._check.load_modules()
            self._fixup.load_modules()

        await self.sys_run_in_executor(_load_modules)

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

    @property
    def suggestions(self) -> list[Suggestion]:
        """Return a list of suggestions that can handled."""
        return self._suggestions

    def add_suggestion(self, suggestion: Suggestion) -> None:
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

        # Event on suggestion added to issue
        for issue in self.issues_for_suggestion(suggestion):
            self.sys_homeassistant.websocket.supervisor_event(
                WSEvent.ISSUE_CHANGED, self._make_issue_message(issue)
            )

    @property
    def unsupported(self) -> list[UnsupportedReason]:
        """Return a list of unsupported reasons."""
        return self._unsupported

    def add_unsupported_reason(self, reason: UnsupportedReason) -> None:
        """Add a reason for unsupported."""
        if reason not in self._unsupported:
            self._unsupported.append(reason)
            self.sys_homeassistant.websocket.supervisor_event(
                WSEvent.SUPPORTED_CHANGED,
                attr.asdict(SupportedChanged(False, self.unsupported)),
            )

    @property
    def unhealthy(self) -> list[UnhealthyReason]:
        """Return a list of unhealthy reasons."""
        return self._unhealthy

    def add_unhealthy_reason(self, reason: UnhealthyReason) -> None:
        """Add a reason for unhealthy."""
        if reason not in self._unhealthy:
            self._unhealthy.append(reason)
            self.sys_homeassistant.websocket.supervisor_event(
                WSEvent.HEALTH_CHANGED,
                attr.asdict(HealthChanged(False, self.unhealthy)),
            )

    def _make_issue_message(self, issue: Issue) -> dict[str, Any]:
        """Make issue into message for core."""
        return attr.asdict(issue) | {
            "suggestions": [
                attr.asdict(suggestion)
                for suggestion in self.suggestions_for_issue(issue)
            ]
        }

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
        reference: str | None = None,
        suggestions: list[SuggestionType] | None = None,
    ) -> None:
        """Create issues and suggestion."""
        self.add_issue(Issue(issue, context, reference), suggestions)

    def add_issue(
        self, issue: Issue, suggestions: list[SuggestionType] | None = None
    ) -> None:
        """Add an issue and suggestions."""
        if suggestions:
            for suggestion in suggestions:
                self.add_suggestion(
                    Suggestion(suggestion, issue.context, issue.reference)
                )

        if issue in self._issues:
            return
        _LOGGER.info(
            "Create new issue %s - %s / %s", issue.type, issue.context, issue.reference
        )
        self._issues.append(issue)

        # Event on issue creation
        self.sys_homeassistant.websocket.supervisor_event(
            WSEvent.ISSUE_CHANGED, self._make_issue_message(issue)
        )

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

        # Event on suggestion removed from issues
        for issue in self.issues_for_suggestion(suggestion):
            self.sys_homeassistant.websocket.supervisor_event(
                WSEvent.ISSUE_CHANGED, self._make_issue_message(issue)
            )

    def dismiss_issue(self, issue: Issue) -> None:
        """Dismiss suggested action."""
        if issue not in self._issues:
            raise ResolutionError(
                f"The UUID {issue.uuid} is not a valid issue", _LOGGER.warning
            )
        self._issues.remove(issue)

        # Event on issue removal
        self.sys_homeassistant.websocket.supervisor_event(
            WSEvent.ISSUE_REMOVED, attr.asdict(issue)
        )

        # Clean up any orphaned suggestions
        for suggestion in self.suggestions_for_issue(issue):
            if not self.issues_for_suggestion(suggestion):
                self.dismiss_suggestion(suggestion)

    def dismiss_unsupported(self, reason: Issue) -> None:
        """Dismiss a reason for unsupported."""
        if reason not in self._unsupported:
            raise ResolutionError(f"The reason {reason} is not active", _LOGGER.warning)
        self._unsupported.remove(reason)
        self.sys_homeassistant.websocket.supervisor_event(
            WSEvent.SUPPORTED_CHANGED,
            attr.asdict(
                SupportedChanged(self.sys_core.supported, self.unsupported or None)
            ),
        )

    def suggestions_for_issue(self, issue: Issue) -> set[Suggestion]:
        """Get suggestions that fix an issue."""
        return {
            suggestion
            for fix in self.fixup.fixes_for_issue(issue)
            for suggestion in fix.all_suggestions
            if suggestion.reference == issue.reference
        }

    def issues_for_suggestion(self, suggestion: Suggestion) -> set[Issue]:
        """Get issues fixed by a suggestion."""
        return {
            issue
            for fix in self.fixup.fixes_for_suggestion(suggestion)
            for issue in fix.all_issues
            if issue.reference == suggestion.reference
        }
