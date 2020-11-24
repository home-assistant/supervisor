"""Helpers to suggestion the system."""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from .suggestions.do_full_snapshot import SuggestionDoFullSnapshot
from .suggestions.clear_full_snapshot import SuggestionClearFullSnapshot

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionSuggestion(CoreSysAttributes):
    """Suggestion class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the suggestion class."""
        self.coresys = coresys

        self._do_full_snapshot = SuggestionDoFullSnapshot(coresys)
        self._clear_full_snapshot = SuggestionClearFullSnapshot(coresys)
