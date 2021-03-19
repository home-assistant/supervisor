"""Helpers to checks the system."""
from importlib import import_module
import logging
from typing import Any, Dict, List

from ..const import ATTR_CHECKS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionNotFound
from .checks.base import CheckBase
from .validate import get_valid_modules

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionCheck(CoreSysAttributes):
    """Checks class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        self.coresys = coresys
        self._checks: Dict[str, CheckBase] = {}

        self._load()

    @property
    def data(self) -> Dict[str, Any]:
        """Return data."""
        return self.sys_resolution.data[ATTR_CHECKS]

    @property
    def all_checks(self) -> List[CheckBase]:
        """Return all list of all checks."""
        return list(self._checks.values())

    def _load(self):
        """Load all checks."""
        package = f"{__package__}.checks"
        for module in get_valid_modules("checks"):
            check_module = import_module(f"{package}.{module}")
            check = check_module.setup(self.coresys)
            self._checks[check.slug] = check

    def get(self, slug: str) -> CheckBase:
        """Return check based on slug."""
        if slug in self._checks:
            return self._checks[slug]

        raise ResolutionNotFound(f"Check with slug {slug} not found!")

    async def check_system(self) -> None:
        """Check the system."""
        _LOGGER.info("Starting system checks with state %s", self.sys_core.state)

        for check in self.all_checks:
            if not check.enabled:
                _LOGGER.warning("Skipping disabled check %s", check.slug)
                continue
            try:
                await check()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.error("Error during processing %s: %s", check.issue, err)
                self.sys_capture_exception(err)

        _LOGGER.info("System checks complete")
