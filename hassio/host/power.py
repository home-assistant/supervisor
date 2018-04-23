"""Power control for host."""

from ..coresys import CoreSysAttributes
from ..exceptions import HassioNotSupportedError


class PowerControl(CoreSysAttributes):
    """Handle host power controls."""

    def __init__(self, coresys):
        """Initialize host power handling."""
        self.coresys = coresys

    def _check_systemd(self):
        """Check if systemd is connect or raise error."""
        if not self.sys_dbus.systemd.is_connected:
            raise HassioNotSupportedError("No systemd connections")

    async def reboot(self):
        """Reboot host system."""
        self._check_systemd()
        try:
            await self.sys_core.shutdown()
        finally:
            await self.sys_dbus.systemd.reboot()

    async def shutdown(self):
        """Shutdown host system."""
        self._check_systemd()
        try:
            await self.sys_core.shutdown()
        finally:
            await self.sys_dbus.systemd.shutdown()
