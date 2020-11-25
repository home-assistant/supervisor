"""Helpers to checks the system."""
import logging
from typing import List

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HassioError
from .checks.base import CheckBase
from .checks.free_space import CheckFreeSpace

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionCheck(CoreSysAttributes):
    """Checks class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        self.coresys = coresys

        self._free_space = CheckFreeSpace(coresys)

    @property
    def all_tests(self) -> List[CheckBase]:
        """Return all list of all checks."""
        return [self._free_space]

    async def check_system(self) -> None:
        """Check the system."""
        _LOGGER.info("Starting system checks with state %s", self.sys_core.state)

        for test in self.all_tests:
            try:
                await test()
            except HassioError as err:
                _LOGGER.warning("Error during processing %s: %s", test.issue, err)
                self.sys_capture_exception(err)

        _LOGGER.info("System checks complete")
