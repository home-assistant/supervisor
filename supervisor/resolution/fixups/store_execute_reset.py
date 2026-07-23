"""Helpers to check and fix issues with free space."""

import logging

from ...coresys import CoreSys
from ...exceptions import (
    ResolutionFixupError,
    ResolutionFixupJobError,
    StoreError,
    StoreInvalidAppRepo,
    StoreNotFound,
)
from ...jobs.const import JobCondition
from ...jobs.decorator import Job
from ..const import ContextType, IssueType, SuggestionType
from ..data import Suggestion
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupStoreExecuteReset(coresys)


class FixupStoreExecuteReset(FixupBase):
    """Storage class for fixup."""

    @Job(
        name="fixup_store_execute_reset_process",
        conditions=[JobCondition.INTERNET_SYSTEM, JobCondition.FREE_SPACE],
        on_condition=ResolutionFixupJobError,
    )
    async def process_fixup(self, suggestion: Suggestion) -> None:
        """Initialize the fixup class."""
        if not suggestion.reference:
            return

        _LOGGER.info("Reset corrupt Store: %s", suggestion.reference)
        try:
            repository = self.sys_store.get(suggestion.reference)
        except StoreNotFound:
            _LOGGER.warning("Can't find store %s for fixup", suggestion.reference)
            return

        try:
            await repository.reset()
        except StoreInvalidAppRepo:
            # The repository re-cloned fine but still isn't valid, so the
            # problem is upstream and retrying won't help. Drop the reset
            # suggestion to stop the hourly auto-retry, while leaving the
            # issue (and its remove suggestion) so the user stays informed.
            self.sys_resolution.dismiss_suggestion(suggestion)
            raise ResolutionFixupError from None
        except StoreError:
            raise ResolutionFixupError from None

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_RESET

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.STORE

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.CORRUPT_REPOSITORY, IssueType.FATAL_ERROR]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
