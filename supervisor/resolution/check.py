"""Helpers to checks the system."""
import logging
import pkgutil
import sys
from typing import Any, Dict, List

from ..const import ATTR_CHECKS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionNotFound
from .checks.base import CHECK_REGISTRY, CheckBase
from .validate import get_valid_modules

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionCheck(CoreSysAttributes):
    """Checks class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        self.coresys = coresys
        self._checks: Dict[str, CheckBase] = {}
        self.load()

    @property
    def data(self) -> Dict[str, Any]:
        """Return data."""
        return self.sys_resolution.data[ATTR_CHECKS]

    @property
    def all_checks(self) -> List[CheckBase]:
        """Return all list of all checks."""
        return list(self._checks.values())

    def load(self):
        """Load all checks."""
        load_from = "checks"
        base_module = f"{__package__}.{load_from}"
        check_modules = get_valid_modules(load_from)
        for check in check_modules:
            full_package_name = f"{base_module}.{check}"
            if full_package_name not in sys.modules:
                pkgutil.find_loader(full_package_name).load_module(full_package_name)

        for check in CHECK_REGISTRY:
            if check.slug not in self._checks:
                check.coresys = self.coresys
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
