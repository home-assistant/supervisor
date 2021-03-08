"""Helpers to checks the system."""
import logging
from typing import Any, Dict, List, Optional

from ..const import ATTR_CHECKS, ATTR_ENABLED
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import ResolutionError
from ..utils.common import FileConfiguration
from .checks.addon_pwned import CheckAddonPwned
from .checks.base import CheckBase
from .checks.core_security import CheckCoreSecurity
from .checks.free_space import CheckFreeSpace
from .const import FILE_CONFIG_CHECK
from .validate import SCHEMA_CHECK_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class ResolutionCheck(FileConfiguration, CoreSysAttributes):
    """Checks class for resolution."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize the checks class."""
        super().__init__(FILE_CONFIG_CHECK, SCHEMA_CHECK_CONFIG)
        self.coresys = coresys

        self._core_security = CheckCoreSecurity(coresys)
        self._free_space = CheckFreeSpace(coresys)
        self._addon_pwned = CheckAddonPwned(coresys)

    @property
    def data(self) -> Dict[str, Any]:
        """Return data."""
        return self._data

    @property
    def all_checks(self) -> List[CheckBase]:
        """Return all list of all checks."""
        return [self._core_security, self._free_space, self._addon_pwned]

    def _get_check(self, name: str) -> Optional[CheckBase]:
        """Return the check matching the name."""
        filtered = [x for x in self.all_checks if x.name == name]
        count = len(filtered)
        if count != 1:
            raise ResolutionError(
                f"Unexpected number of checks matching {name}, result was {count}"
            )
        return filtered[0]

    async def check_system(self) -> None:
        """Check the system."""
        _LOGGER.info("Starting system checks with state %s", self.sys_core.state)

        for check in self.all_checks:
            if not check.enabled:
                _LOGGER.info("Skipping disabled check %s", check.name)
                continue
            try:
                await check()
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.warning("Error during processing %s: %s", check.issue, err)
                self.sys_capture_exception(err)

        _LOGGER.info("System checks complete")

    def disable(self, name: str) -> None:
        """Disable check."""
        check = self._get_check(name)
        if not check.can_disable:
            raise ResolutionError(f"{check.name} can not be disabled", _LOGGER.error)

        if not check.enabled:
            return
        self._data[ATTR_CHECKS][name] = {ATTR_ENABLED: False}
        self.save_data()

    def enable(self, name: str) -> None:
        """Enable check."""
        check = self._get_check(name)
        if check.enabled:
            return
        self._data[ATTR_CHECKS][name] = {ATTR_ENABLED: True}
        self.save_data()
