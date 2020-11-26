"""Baseclass for system fixup."""
from abc import ABC, abstractmethod, abstractproperty
from contextlib import suppress
import logging
from typing import Optional

from ...coresys import CoreSys, CoreSysAttributes
from ...exceptions import ResolutionError, ResolutionFixupError
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue, Suggestion

_LOGGER: logging.Logger = logging.getLogger(__name__)


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

        if self.issue is None:
            return

        with suppress(ResolutionError):
            self.sys_resolution.dismiss_issue(
                Issue(self.issue, self.context, fixing_suggestion.reference)
            )

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
    def issue(self) -> Optional[IssueType]:
        """Return a IssueType enum."""
        return None

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
