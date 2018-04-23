"""Power control for host."""
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import HostNotSupportedError

_LOGGER = logging.getLogger(__name__)


class PowerControl(CoreSysAttributes):
    """Handle host power controls."""

    def __init__(self, coresys):
        """Initialize host power handling."""
        self.coresys = coresys

    def _check_systemd(self):
        """Check if systemd is connect or raise error."""
        if not self.sys_dbus.systemd.is_connected:
            _LOGGER.error("No systemd dbus connection available")
            raise HostNotSupportedError()

    async def reboot(self):
        """Reboot host system."""
        self._check_systemd()

        _LOGGER.info("Initialize host reboot over systemd")
        try:
            await self.sys_core.shutdown()
        finally:
            await self.sys_dbus.systemd.reboot()

    async def shutdown(self):
        """Shutdown host system."""
        self._check_systemd()

        _LOGGER.info("Initialize host power off over systemd")
        try:
            await self.sys_core.shutdown()
        finally:
            await self.sys_dbus.systemd.power_off()
