"""Fetch last versions from webserver."""

from __future__ import annotations

import logging

from ..const import ATTR_FORCE_SECURITY, ATTR_PWNED, FILE_HASSIO_SECURITY
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import PwnedError
from ..utils.common import FileConfiguration
from ..utils.pwned import check_pwned_password
from ..validate import SCHEMA_SECURITY_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class Security(FileConfiguration, CoreSysAttributes):
    """Handle Security properties."""

    def __init__(self, coresys: CoreSys):
        """Initialize updater."""
        super().__init__(FILE_HASSIO_SECURITY, SCHEMA_SECURITY_CONFIG)
        self.coresys = coresys

    @property
    def force(self) -> bool:
        """Return if force security is enabled/disabled."""
        return self._data[ATTR_FORCE_SECURITY]

    @force.setter
    def force(self, value: bool) -> None:
        """Set force security is enabled/disabled."""
        self._data[ATTR_FORCE_SECURITY] = value

    @property
    def pwned(self) -> bool:
        """Return if pwned is enabled/disabled."""
        return self._data[ATTR_PWNED]

    @pwned.setter
    def pwned(self, value: bool) -> None:
        """Set pwned is enabled/disabled."""
        self._data[ATTR_PWNED] = value

    async def verify_secret(self, pwned_hash: str) -> None:
        """Verify pwned state of a secret."""
        if not self.pwned:
            _LOGGER.warning("Disabled pwned, skip validation")
            return

        try:
            await check_pwned_password(self.sys_websession, pwned_hash)
        except PwnedError:
            if self.force:
                raise
            return
