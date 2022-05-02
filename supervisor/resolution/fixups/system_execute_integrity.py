"""Helpers to check and fix issues with free space."""
import logging
from typing import Optional

from ...coresys import CoreSys
from ...exceptions import ResolutionFixupError, ResolutionFixupJobError
from ...jobs.const import JobCondition
from ...jobs.decorator import Job
from ...security.const import ContentTrustResult
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupSystemExecuteIntegrity(coresys)


class FixupSystemExecuteIntegrity(FixupBase):
    """Storage class for fixup."""

    @Job(
        conditions=[JobCondition.INTERNET_SYSTEM],
        on_condition=ResolutionFixupJobError,
    )
    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        result = await self.sys_security.integrity_check()

        if ContentTrustResult.FAILED in (result.core, result.supervisor):
            raise ResolutionFixupError()

        for plugin in result.plugins:
            if plugin != ContentTrustResult.FAILED:
                continue
            raise ResolutionFixupError()

        for addon in result.addons:
            if addon != ContentTrustResult.FAILED:
                continue
            raise ResolutionFixupError()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_INTEGRITY

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.SYSTEM

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.TRUST]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
