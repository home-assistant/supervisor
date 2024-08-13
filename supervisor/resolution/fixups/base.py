"""Baseclass for system fixup."""

from abc import ABC, abstractmethod
import logging

from ...coresys import CoreSys, CoreSysAttributes
from ...exceptions import ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue, Suggestion

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupBase(ABC, CoreSysAttributes):
    """Baseclass for fixup."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the fixup class."""
        self.coresys = coresys

    async def __call__(self, fixing_suggestion: Suggestion | None = None) -> None:
        """Execute the evaluation."""
        if not fixing_suggestion:
            # Get suggestion to fix
            fixing_suggestion: Suggestion | None = next(
                iter(self.all_suggestions), None
            )

        # No suggestion
        if fixing_suggestion is None:
            return

        # Process fixup
        _LOGGER.debug("Run fixup for %s/%s", self.suggestion, self.context)
        try:
            await self.process_fixup(reference=fixing_suggestion.reference)
        except ResolutionFixupError:
            return

        # Cleanup issue
        for issue in self.sys_resolution.issues_for_suggestion(fixing_suggestion):
            self.sys_resolution.dismiss_issue(issue)

        if fixing_suggestion in self.sys_resolution.suggestions:
            self.sys_resolution.dismiss_suggestion(fixing_suggestion)

    @abstractmethod
    async def process_fixup(self, reference: str | None = None) -> None:
        """Run processing of fixup."""

    @property
    @abstractmethod
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""

    @property
    @abstractmethod
    def context(self) -> ContextType:
        """Return a ContextType enum."""

    @property
    @abstractmethod
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False

    @property
    def all_suggestions(self) -> list[Suggestion]:
        """List of all suggestions which when applied run this fixup."""
        return [
            suggestion
            for suggestion in self.sys_resolution.suggestions
            if suggestion.type == self.suggestion and suggestion.context == self.context
        ]

    @property
    def all_issues(self) -> list[Issue]:
        """List of all issues which could be fixed by this fixup."""
        return [
            issue
            for issue in self.sys_resolution.issues
            if issue.type in self.issues and issue.context == self.context
        ]

    @property
    def slug(self) -> str:
        """Return the check slug."""
        return self.__class__.__module__.rsplit(".", maxsplit=1)[-1]
