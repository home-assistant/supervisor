"""Helpers to check and fix issues with free space."""
import logging
from typing import List, Optional

from supervisor.exceptions import ResolutionFixupError, StoreError, StoreNotFound

from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupStoreExecuteRemove(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Remove invalid Store: %s", reference)
        try:
            repository = self.sys_store.get(reference)
        except StoreNotFound:
            _LOGGER.warning("Can't find store %s for fixup", reference)
            return

        # Remove repository
        try:
            await repository.remove()
        except StoreError:
            raise ResolutionFixupError() from None
        else:
            self.sys_store.repositories.pop(repository.slug, None)

        self.sys_config.drop_addon_repository(repository.source)
        self.sys_config.save_data()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.EXECUTE_REMOVE

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.STORE

    @property
    def issues(self) -> List[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.CORRUPT_REPOSITORY]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
