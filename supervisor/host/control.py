"""Power control for host."""
import logging

from ..coresys import CoreSysAttributes
from ..exceptions import HostNotSupportedError

_LOGGER: logging.Logger = logging.getLogger(__name__)

MANAGER = "manager"
HOSTNAME = "hostname"


class SystemControl(CoreSysAttributes):
    """Handle host power controls."""

    def __init__(self, coresys):
        """Initialize host power handling."""
        self.coresys = coresys

    def _check_dbus(self, flag):
        """Check if systemd is connect or raise error."""
        if flag == MANAGER and (
            self.sys_dbus.systemd.is_connected or self.sys_dbus.logind.is_connected
        ):
            return
        if flag == HOSTNAME and self.sys_dbus.hostname.is_connected:
            return

        _LOGGER.error("No %s D-Bus connection available", flag)
        raise HostNotSupportedError()

    async def reboot(self):
        """Reboot host system."""
        self._check_dbus(MANAGER)

        use_logind = self.sys_dbus.logind.is_connected
        _LOGGER.info(
            "Initialize host reboot using %s", "logind" if use_logind else "systemd"
        )

        try:
            await self.sys_core.shutdown()
        finally:
            if use_logind:
                await self.sys_dbus.logind.reboot()
            else:
                await self.sys_dbus.systemd.reboot()

    async def shutdown(self):
        """Shutdown host system."""
        self._check_dbus(MANAGER)

        use_logind = self.sys_dbus.logind.is_connected
        _LOGGER.info(
            "Initialize host power off %s", "logind" if use_logind else "systemd"
        )

        try:
            await self.sys_core.shutdown()
        finally:
            if use_logind:
                await self.sys_dbus.logind.power_off()
            else:
                await self.sys_dbus.systemd.power_off()

    async def set_hostname(self, hostname):
        """Set local a new Hostname."""
        self._check_dbus(HOSTNAME)

        _LOGGER.info("Set hostname %s", hostname)
        await self.sys_dbus.hostname.set_static_hostname(hostname)
        await self.sys_host.info.update()
