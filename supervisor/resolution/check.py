"""Helpers to checks the system."""
import logging
from typing import Any, Dict, List

from ..const import ATTR_CHECKS
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionNotFound
from .checks.addon_pwned import CheckAddonPwned
from .checks.base import CheckBase
from .checks.core_security import CheckCoreSecurity
from .checks.free_space import CheckFreeSpace

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionCheck(CoreSysAttributes):
    """Checks class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        self.coresys = coresys
        self._core_security = CheckCoreSecurity(coresys)
        self._free_space = CheckFreeSpace(coresys)
        self._addon_pwned = CheckAddonPwned(coresys)

    @property
    def data(self) -> Dict[str, Any]:
        """Return data."""
        return self.sys_resolution.data[ATTR_CHECKS]

    @property
    def all_checks(self) -> List[CheckBase]:
        """Return all list of all checks."""
        return [self._core_security, self._free_space, self._addon_pwned]

    def get(self, slug: str) -> CheckBase:
        """Return check based on slug."""
        for check in self.all_checks:
            if slug != check.slug:
                continue
            return check
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
