"""Baseclass for system fixup."""
from abc import ABC, abstractmethod, abstractproperty
import logging
from typing import List, Optional

from ...coresys import CoreSys, CoreSysAttributes
from ...exceptions import ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue, Suggestion

_LOGGER: logging.Logger = logging.getLogger(__package__)


class FixupBase(ABC, CoreSysAttributes):
    """Baseclass for fixup."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the fixup class."""
        self.coresys = coresys

    async def __call__(self) -> None:
        """Execute the evaluation."""
        # Get suggestion to fix
        fixing_suggestion: Optional[Suggestion] = None
        for suggestion in self.sys_resolution.suggestions:
            if suggestion.type != self.suggestion or suggestion.context != self.context:
                continue
            fixing_suggestion = suggestion
            break

        # No suggestion
        if fixing_suggestion is None:
            return

        # Process fixup
        _LOGGER.debug("Run fixup for %s/%s", self.suggestion, self.context)
        try:
            await self.process_fixup(reference=fixing_suggestion.reference)
        except ResolutionFixupError:
            return

        self.sys_resolution.dismiss_suggestion(fixing_suggestion)

        # Cleanup issue
        for issue_type in self.issues:
            issue = Issue(issue_type, self.context, fixing_suggestion.reference)
            if issue not in self.sys_resolution.issues:
                continue
            self.sys_resolution.dismiss_issue(issue)

    @abstractmethod
    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Run processing of fixup."""

    @property
    @abstractproperty
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""

    @property
    @abstractproperty
    def context(self) -> ContextType:
        """Return a ContextType enum."""

    @property
    def issues(self) -> List[IssueType]:
        """Return a IssueType enum list."""
        return []

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
