"""Helpers to check and fix issues with free space."""

import logging

from ...coresys import CoreSys
from ...exceptions import (
    ResolutionFixupError,
    ResolutionFixupJobError,
    StoreError,
    StoreNotFound,
)
from ...jobs.const import JobCondition
from ...jobs.decorator import Job
from ..const import ContextType, IssueType, SuggestionType
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
    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        if not reference:
            return

        _LOGGER.info("Reset corrupt Store: %s", reference)
        try:
            repository = self.sys_store.get(reference)
        except StoreNotFound:
            _LOGGER.warning("Can't find store %s for fixup", reference)
            return

        # Local add-ons are not a git repo, can't remove and re-pull
        try:
            if repository.git:
                await repository.git.reset()

            # Load data again
            await repository.load()
        except StoreError:
            raise ResolutionFixupError() from None

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
