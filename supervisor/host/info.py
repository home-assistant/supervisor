"""Info control for host."""

import asyncio
from datetime import datetime, tzinfo
import logging

from ..coresys import CoreSysAttributes
from ..dbus.const import MulticastProtocolEnabled
from ..exceptions import DBusError, HostError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class InfoCenter(CoreSysAttributes):
    """Handle local system information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys

    @property
    def hostname(self) -> str | None:
        """Return local hostname."""
        return self.sys_dbus.hostname.hostname

    @property
    def llmnr_hostname(self) -> str | None:
        """Return local llmnr hostname."""
        return self.sys_dbus.resolved.llmnr_hostname

    @property
    def broadcast_llmnr(self) -> bool | None:
        """Host is broadcasting llmnr name."""
        if self.sys_dbus.resolved.llmnr:
            return self.sys_dbus.resolved.llmnr == MulticastProtocolEnabled.YES
        return None

    @property
    def broadcast_mdns(self) -> bool | None:
        """Host is broadcasting mdns name."""
        if self.sys_dbus.resolved.multicast_dns:
            return self.sys_dbus.resolved.multicast_dns == MulticastProtocolEnabled.YES
        return None

    @property
    def chassis(self) -> str | None:
        """Return local chassis type."""
        return self.sys_dbus.hostname.chassis

    @property
    def deployment(self) -> str | None:
        """Return local deployment type."""
        return self.sys_dbus.hostname.deployment

    @property
    def kernel(self) -> str | None:
        """Return local kernel version."""
        return self.sys_dbus.hostname.kernel

    @property
    def operating_system(self) -> str | None:
        """Return local operating system."""
        return self.sys_dbus.hostname.operating_system

    @property
    def cpe(self) -> str | None:
        """Return local CPE."""
        return self.sys_dbus.hostname.cpe

    @property
    def timezone(self) -> str | None:
        """Return host timezone."""
        return self.sys_dbus.timedate.timezone

    @property
    def timezone_tzinfo(self) -> tzinfo | None:
        """Return host timezone as tzinfo object."""
        return self.sys_dbus.timedate.timezone_tzinfo

    @property
    def dt_utc(self) -> datetime | None:
        """Return host UTC time."""
        return self.sys_dbus.timedate.dt_utc

    @property
    def use_rtc(self) -> bool | None:
        """Return true if host have an RTC."""
        return self.sys_dbus.timedate.local_rtc

    @property
    def use_ntp(self) -> bool | None:
        """Return true if host using NTP."""
        return self.sys_dbus.timedate.ntp

    @property
    def dt_synchronized(self) -> bool | None:
        """Return true if host time is syncronized."""
        return self.sys_dbus.timedate.ntp_synchronized

    @property
    def startup_time(self) -> float | None:
        """Return startup time in seconds."""
        return self.sys_dbus.systemd.startup_time

    @property
    def boot_timestamp(self) -> int | None:
        """Return the boot timestamp."""
        return self.sys_dbus.systemd.boot_timestamp

    @property
    def virtualization(self) -> str | None:
        """Return virtualization hypervisor being used."""
        return self.sys_dbus.systemd.virtualization

    async def total_space(self) -> float:
        """Return total space (GiB) on disk for supervisor data directory."""
        return await self.sys_run_in_executor(
            self.sys_hardware.disk.get_disk_total_space,
            self.coresys.config.path_supervisor,
        )

    async def used_space(self) -> float:
        """Return used space (GiB) on disk for supervisor data directory."""
        return await self.sys_run_in_executor(
            self.sys_hardware.disk.get_disk_used_space,
            self.coresys.config.path_supervisor,
        )

    async def free_space(self) -> float:
        """Return available space (GiB) on disk for supervisor data directory."""
        return await self.sys_run_in_executor(
            self.sys_hardware.disk.get_disk_free_space,
            self.coresys.config.path_supervisor,
        )

    async def disk_life_time(self) -> float | None:
        """Return the estimated life-time usage (in %) of the SSD storing the data directory."""
        return await self.sys_run_in_executor(
            self.sys_hardware.disk.get_disk_life_time,
            self.coresys.config.path_supervisor,
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
            raise HostError(f"Can't read kernel log: {err}", _LOGGER.error) from err

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
            if self.sys_dbus.resolved.is_connected:
                await self.sys_dbus.resolved.update()
        except DBusError:
            _LOGGER.warning("Can't update host system information!")
