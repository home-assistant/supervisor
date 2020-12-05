"""Helpers to fixup the system."""
import logging
from typing import List

from ..coresys import CoreSys, CoreSysAttributes
from .data import Suggestion
from .fixups.base import FixupBase
from .fixups.clear_full_snapshot import FixupClearFullSnapshot
from .fixups.create_full_snapshot import FixupCreateFullSnapshot
from .fixups.store_execute_reload import FixupStoreExecuteReload
from .fixups.store_execute_remove import FixupStoreExecuteRemove
from .fixups.store_execute_reset import FixupStoreExecuteReset

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionFixup(CoreSysAttributes):
    """Suggestion class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the suggestion class."""
        self.coresys = coresys

        self._create_full_snapshot = FixupCreateFullSnapshot(coresys)
        self._clear_full_snapshot = FixupClearFullSnapshot(coresys)
        self._store_execute_reset = FixupStoreExecuteReset(coresys)
        self._store_execute_reload = FixupStoreExecuteReload(coresys)
        self._store_execute_remove = FixupStoreExecuteRemove(coresys)

    @property
    def all_fixes(self) -> List[FixupBase]:
        """Return a list of all fixups.

        Order can be important!
        """
        return [
            self._create_full_snapshot,
            self._clear_full_snapshot,
            self._store_execute_reload,
            self._store_execute_reset,
            self._store_execute_remove,
        ]

    async def run_autofix(self) -> None:
        """Run all startup fixes."""
        _LOGGER.info("Starting system autofix at state %s", self.sys_core.state)

        for fix in self.all_fixes:
            if not fix.auto:
                continue
            try:
                await fix()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Error during processing %s: %s", fix.suggestion, err)
                self.sys_capture_exception(err)

        _LOGGER.info("System autofix complete")

    async def apply_fixup(self, suggestion: Suggestion) -> None:
        """Apply a fixup for a suggestion."""
        for fix in self.all_fixes:
            if fix.suggestion != suggestion.type or fix.context != suggestion.context:
                continue
            await fix()
