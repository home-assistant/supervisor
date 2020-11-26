"""Helpers to check and fix issues with free space."""
import logging
from typing import Optional

from supervisor.exceptions import ResolutionFixupError, StoreError, StoreNotFound

from ...utils import remove_folder
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupCreateFullSnapshot(FixupBase):
    """Storage class for fixup."""

    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        _LOGGER.info("Reset corrupt Store: %s", reference)
        try:
            repository = self.sys_store.get(reference)
        except StoreNotFound:
            _LOGGER.error("Can't find store %s for fixup", reference)
            return

        await remove_folder(repository.git.path)

        # Load data again
        try:
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
    def issue(self) -> IssueType:
        """Return a IssueType enum."""
        return IssueType.CORRUPT_REPOSITORY

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
