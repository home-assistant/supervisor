"""Power control for host."""
from datetime import datetime
import logging

from ..const import HostFeature
from ..coresys import CoreSysAttributes
from ..exceptions import HostNotSupportedError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SystemControl(CoreSysAttributes):
    """Handle host power controls."""

    def __init__(self, coresys):
        """Initialize host power handling."""
        self.coresys = coresys

    def _check_dbus(self, flag: HostFeature) -> None:
        """Check if systemd is connect or raise error."""
        if flag in (HostFeature.SHUTDOWN, HostFeature.REBOOT) and (
            self.sys_dbus.systemd.is_connected or self.sys_dbus.logind.is_connected
        ):
            return
        if flag == HostFeature.HOSTNAME and self.sys_dbus.hostname.is_connected:
            return
        if flag == HostFeature.TIMEDATE and self.sys_dbus.timedate.is_connected:
            return

        raise HostNotSupportedError(
            f"No {flag!s} D-Bus connection available", _LOGGER.error
        )

    async def reboot(self) -> None:
        """Reboot host system."""
        self._check_dbus(HostFeature.REBOOT)

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

    async def shutdown(self) -> None:
        """Shutdown host system."""
        self._check_dbus(HostFeature.SHUTDOWN)

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

    async def set_hostname(self, hostname: str) -> None:
        """Set local a new Hostname."""
        self._check_dbus(HostFeature.HOSTNAME)

        _LOGGER.info("Set hostname %s", hostname)
        await self.sys_dbus.hostname.set_static_hostname(hostname)
        await self.sys_dbus.hostname.update()

    async def set_datetime(self, new_time: datetime) -> None:
        """Update host clock with new (utc) datetime."""
        self._check_dbus(HostFeature.TIMEDATE)

        _LOGGER.info("Setting new host datetime: %s", new_time.isoformat())
        await self.sys_dbus.timedate.set_time(new_time)
        await self.sys_dbus.timedate.update()
