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
    return FixupStoreExecuteReload(coresys)


class FixupStoreExecuteReload(FixupBase):
    """Storage class for fixup."""

    @Job(
        name="fixup_store_execute_reload_process",
        conditions=[JobCondition.INTERNET_SYSTEM, JobCondition.FREE_SPACE],
        on_condition=ResolutionFixupJobError,
    )
    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Reload Store: %s", reference)
        try:
            repository = self.sys_store.get(reference)
        except StoreNotFound:
            _LOGGER.warning("Can't find store %s for fixup", reference)
            return

        # Load data again
        try:
            await repository.load()
            await self.sys_store.reload(repository)
        except StoreError:
            raise ResolutionFixupError() from None

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_RELOAD

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.STORE

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.FATAL_ERROR]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
