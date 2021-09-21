"""Info control for host."""
import asyncio
from datetime import datetime
import logging
from typing import Optional

from ..coresys import CoreSysAttributes
from ..exceptions import DBusError, HostError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class InfoCenter(CoreSysAttributes):
    """Handle local system information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys

    @property
    def hostname(self) -> Optional[str]:
        """Return local hostname."""
        return self.sys_dbus.hostname.hostname

    @property
    def chassis(self) -> Optional[str]:
        """Return local chassis type."""
        return self.sys_dbus.hostname.chassis

    @property
    def deployment(self) -> Optional[str]:
        """Return local deployment type."""
        return self.sys_dbus.hostname.deployment

    @property
    def kernel(self) -> Optional[str]:
        """Return local kernel version."""
        return self.sys_dbus.hostname.kernel

    @property
    def operating_system(self) -> Optional[str]:
        """Return local operating system."""
        return self.sys_dbus.hostname.operating_system

    @property
    def cpe(self) -> Optional[str]:
        """Return local CPE."""
        return self.sys_dbus.hostname.cpe

    @property
    def timezone(self) -> Optional[str]:
        """Return host timezone."""
        return self.sys_dbus.timedate.timezone

    @property
    def dt_utc(self) -> Optional[datetime]:
        """Return host UTC time."""
        return self.sys_dbus.timedate.dt_utc

    @property
    def use_rtc(self) -> Optional[bool]:
        """Return true if host have an RTC."""
        return self.sys_dbus.timedate.local_rtc

    @property
    def use_ntp(self) -> Optional[bool]:
        """Return true if host using NTP."""
        return self.sys_dbus.timedate.ntp

    @property
    def dt_synchronized(self) -> Optional[bool]:
        """Return true if host time is syncronized."""
        return self.sys_dbus.timedate.ntp_synchronized

    @property
    def startup_time(self) -> Optional[float]:
        """Return startup time in seconds."""
        return self.sys_dbus.systemd.startup_time

    @property
    def total_space(self) -> float:
        """Return total space (GiB) on disk for supervisor data directory."""
        return self.sys_hardware.disk.get_disk_total_space(
            self.coresys.config.path_supervisor
        )

    @property
    def used_space(self) -> float:
        """Return used space (GiB) on disk for supervisor data directory."""
        return self.sys_hardware.disk.get_disk_used_space(
            self.coresys.config.path_supervisor
        )

    @property
    def free_space(self) -> float:
        """Return available space (GiB) on disk for supervisor data directory."""
        return self.sys_hardware.disk.get_disk_free_space(
            self.coresys.config.path_supervisor
        )

    @property
    def disk_life_time(self) -> float:
        """Return the estimated life-time usage (in %) of the SSD storing the data directory."""
        return self.sys_hardware.disk.get_disk_life_time(
            self.coresys.config.path_supervisor
        )

    async def get_dmesg(self) -> bytes:
        """Return host dmesg output."""
        proc = await asyncio.create_subprocess_shell(
            "dmesg", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        # Get kernel log
        try:
            stdout, _ = await proc.communicate()
        except OSError as err:
            _LOGGER.error("Can't read kernel log: %s", err)
            raise HostError() from err

        return stdout

    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Updating local host information")
        try:
            if self.sys_dbus.hostname.is_connected:
                await self.sys_dbus.hostname.update()
            if self.sys_dbus.timedate.is_connected:
                await self.sys_dbus.timedate.update()
            if self.sys_dbus.systemd.is_connected:
                await self.sys_dbus.systemd.update()
        except DBusError:
            _LOGGER.warning("Can't update host system information!")
