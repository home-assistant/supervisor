"""Fixup class for checking custom repositories."""
import logging
from typing import List, Optional

from ...exceptions import StoreError, StoreNotFound
from ..const import ContextType, IssueType, SuggestionType
from .base import FixupBase

_LOGGER: logging.Logger = logging.getLogger(__name__)


class FixupStoreCheckCustom(FixupBase):
    """Fixup class for checking custom repositories."""

    async def process_fixup(self, reference: Optional[str] = None) -> None:
        """Initialize the fixup class."""
        # Handle non-exsisting repos (wrong URL)
        for repo in list(self.sys_config.addons_repositories):
            _LOGGER.debug("Checking if %s exsist", repo)
            try:
                self.sys_store.get_from_url(repo)
            except StoreNotFound:
                _LOGGER.warning(
                    "Removing custom repository '%s', this does not exsist!", repo
                )
                self.sys_config.drop_addon_repository(repo)

        # Handle broken repositories
        for repo in list(self.sys_config.addons_repositories):
            _LOGGER.debug("Checking if %s is broken", repo)
            repository = self.sys_store.get_from_url(repo)
            try:
                await repository.load()
            except StoreError:
                _LOGGER.warning(
                    "Custom repository '%s', is broken, marked for removal", repo
                )
                self.sys_resolution.create_issue(
                    IssueType.CORRUPT_REPOSITORY,
                    ContextType.STORE,
                    reference=repository.slug,
                    suggestions=[SuggestionType.EXECUTE_REMOVE],
                )

        self.sys_config.save_data()

    @property
    def suggestion(self) -> SuggestionType:
        """Return a SuggestionType enum."""
        return SuggestionType.CUSTOM_REPOSITORIES_CHECK

    @property
    def context(self) -> ContextType:
        """Return a ContextType enum."""
        return ContextType.STORE

    @property
    def issues(self) -> List[IssueType]:
        """Return a IssueType enum list."""
        return [IssueType.CUSTOM_REPOSITORY]

    @property
    def auto(self) -> bool:
        """Return if a fixup can be apply as auto fix."""
        return True
