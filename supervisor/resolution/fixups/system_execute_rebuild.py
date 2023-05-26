"""Helper to fix an issue with the system by rebuilding containers."""

import asyncio

from ...coresys import CoreSys
from ..const import ContextType, IssueType, SuggestionType
from ..data import Issue
from .base import FixupBase


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemExecuteRebuild(coresys)


class FixupSystemExecuteRebuild(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Rebuild containers with docker config issues."""
        await asyncio.gather(
            *[
                self.sys_resolution.apply_suggestion(suggestion)
                for issue in self.current_issues
                for suggestion in self.sys_resolution.suggestions_for_issue(issue)
                if suggestion.type == SuggestionType.EXECUTE_REBUILD
            ]
        )

    @property
    def current_issues(self) -> set[Issue]:
        """List of current docker config issues, excluding the system one."""
        return {
            issue
            for issue in self.sys_resolution.issues
            if issue.type == IssueType.DOCKER_CONFIG and issue.context != self.context
        }

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REBUILD

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.DOCKER_CONFIG]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
