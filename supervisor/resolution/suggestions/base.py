"""Baseclass for system suggestion."""
from abc import ABC, abstractproperty, abstractmethod
import logging
from typing import List

from ...const import CoreState
from ...coresys import CoreSys, CoreSysAttributes
from ..const import SuggestionType

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SuggestionBase(ABC, CoreSysAttributes):
    """Baseclass for suggestion."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the suggestion class."""
        self.coresys = coresys

    @abstractmethod
    async def process_suggestion(self):
        """Run processing of suggestion."""

    @property
    @abstractproperty
    def suggestion(self) -> SuggestionType:
        """Return a Suggestion enum."""

    @property
    def auto(self) -> bool:
        """Return if a suggestion can be apply as auto fix."""
        return False
