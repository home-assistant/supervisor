"""Helpers to fixup the system."""
from importlib import import_module
import logging

from ..coresys import CoreSys, CoreSysAttributes
from ..jobs.const import JobCondition
from ..jobs.decorator import Job
from .data import Issue, Suggestion
from .fixups.base import FixupBase
from .validate import get_valid_modules

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionFixup(CoreSysAttributes):
    """Suggestion class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the suggestion class."""
        self.coresys = coresys
        self._fixups: dict[str, FixupBase] = {}

        self._load()

    def _load(self):
        """Load all checks."""
        package = f"{__package__}.fixups"
        for module in get_valid_modules("fixups"):
            fixup_module = import_module(f"{package}.{module}")
            fixup = fixup_module.setup(self.coresys)
            self._fixups[fixup.slug] = fixup

    @property
    def all_fixes(self) -> list[FixupBase]:
        """Return a list of all fixups."""
        return list(self._fixups.values())

    @Job(conditions=[JobCondition.HEALTHY, JobCondition.RUNNING])
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

    def fixes_for_suggestion(self, suggestion: Suggestion) -> list[FixupBase]:
        """Get fixups to run if the suggestion is applied."""
        return [
            fix
            for fix in self.all_fixes
            if fix.suggestion == suggestion.type and fix.context == suggestion.context
        ]

    def fixes_for_issue(self, issue: Issue) -> list[FixupBase]:
        """Get fixups that would fix the issue if run."""
        return [
            fix
            for fix in self.all_fixes
            if issue.type in fix.issues and issue.context == fix.context
        ]

    async def apply_fixup(self, suggestion: Suggestion) -> None:
        """Apply a fixup for a suggestion."""
        for fix in self.fixes_for_suggestion(suggestion):
            await fix(suggestion)
