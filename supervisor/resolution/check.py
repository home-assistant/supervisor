"""Helpers to checks the system."""
import logging

from ..coresys import CoreSys, CoreSysAttributes
from .checks.free_space import CheckFreeSpace

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionCheck(CoreSysAttributes):
    """Checks class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        self.coresys = coresys

        self._free_space = CheckFreeSpace(coresys)

    async def check_system(self) -> None:
        """Check the system."""
        _LOGGER.info("Starting system checks with state %s", self.sys_core.state)
        await self._free_space()

        _LOGGER.info("System check complete")
