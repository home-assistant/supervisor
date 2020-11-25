"""Helpers to fixup the system."""
import logging
from typing import List

from supervisor.exceptions import HassioError
from supervisor.resolution.data import Suggestion

from ..coresys import CoreSys, CoreSysAttributes
from .fixups.base import FixupBase
from .fixups.clear_full_snapshot import FixupClearFullSnapshot
from .fixups.do_full_snapshot import FixupDoFullSnapshot

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionFixup(CoreSysAttributes):
    """Suggestion class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the suggestion class."""
        self.coresys = coresys

        self._do_full_snapshot = FixupDoFullSnapshot(coresys)
        self._clear_full_snapshot = FixupClearFullSnapshot(coresys)

    @property
    def all_fixes(self) -> List[FixupBase]:
        """Return a list of all fixups."""
        return [self._do_full_snapshot, self._clear_full_snapshot]

    async def run_autofix(self) -> None:
        """Run all startup fixes."""
        _LOGGER.info("Starting system autofix at state %s", self.sys_core.state)

        for fix in self.all_fixes:
            if not fix.auto:
                continue
            try:
                await fix()
            except HassioError as err:
                _LOGGER.warning("Error during processing %s: %s", fix.suggestion, err)
                self.sys_capture_exception(err)

        _LOGGER.info("System autofix complete")

    async def apply_fixup(self, suggestion: Suggestion) -> None:
        """Apply a fixup for a suggestion."""
        for fix in self.all_fixes:
            if fix.suggestion != suggestion.type and fix.context != suggestion.context:
                continue
            await fix()
