"""Helpers to check and fix issues with free space."""

import logging

from ...coresys import CoreSys
from ...exceptions import ResolutionFixupError, StoreError, StoreNotFound
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


def setup(coresys: CoreSys) -> FixupBase:
    """Check setup function."""
    return FixupStoreExecuteRemove(coresys)


class FixupStoreExecuteRemove(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: str | None = None) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Remove invalid Store: %s", reference)
        try:
            repository = self.sys_store.get(reference)
        except StoreNotFound:
            _LOGGER.warning("Can't find store %s for fixup", reference)
            return

        # Remove repository
        try:
            await self.sys_store.remove_repository(repository)
        except StoreError:
            raise ResolutionFixupError() from None

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REMOVE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.STORE

    @property
    def issues(self) -> list[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.CORRUPT_REPOSITORY]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return False
