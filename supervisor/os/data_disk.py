"""Home Assistant Operating-System DataDisk."""
import logging
from pathlib import Path
from typing import Optional

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import (
    DBusError,
    HardwareNotFound,
    HassOSDataDiskError,
    HassOSError,
    HassOSJobError,
    HostError,
)
from ..hardware.const import UdevSubsystem
from ..jobs.const import JobCondition, JobExecutionLimit
from ..jobs.decorator import Job

_LOGGER: logging.Logger = logging.getLogger(__name__)


class DataDisk(CoreSysAttributes):
    """Handle DataDisk feature from OS."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize DataDisk."""
        self.coresys = coresys

    @property
    def disk_used(self) -> Optional[Path]:
        """Return Path to used Disk for data."""
        return self.sys_dbus.agent.datadisk.current_device

    @Job(conditions=[JobCondition.OS_AGENT])
    async def load(self) -> None:
        """Load DataDisk feature."""
        # Update datadisk details on OS-Agent
        if self.sys_dbus.agent.version >= AwesomeVersion("1.2.0"):
            await self.sys_dbus.agent.datadisk.reload_device()

    @Job(
        conditions=[JobCondition.HAOS, JobCondition.OS_AGENT, JobCondition.HEALTHY],
        limit=JobExecutionLimit.ONCE,
        on_condition=HassOSJobError,
    )
    async def migrate_disk(self, new_disk: Path) -> None:
        """Move data partition to a new disk."""
        # Validate integrity of the data input
        try:
            device = self.sys_hardware.get_by_path(new_disk)
        except HardwareNotFound:
            raise HassOSDataDiskError(
                f"'{new_disk!s}' don't exists on the host!", _LOGGER.error
            ) from None

        if device.subsystem != UdevSubsystem.DISK:
            raise HassOSDataDiskError(
                f"'{new_disk!s}' is not a harddisk!", _LOGGER.error
            )
        if self.sys_hardware.disk.is_system_partition(device):
            raise HassOSDataDiskError(
                f"'{new_disk}' is a system disk and can't be used!", _LOGGER.error
            )

        # Migrate data on Host
        try:
            await self.sys_dbus.agent.datadisk.change_device(new_disk)
        except DBusError as err:
            raise HassOSDataDiskError(
                f"Can't move data partition to {new_disk!s}: {err!s}", _LOGGER.error
            ) from err

        # Restart Host for finish the process
        try:
            await self.sys_host.control.reboot()
        except HostError as err:
            raise HassOSError(
                f"Can't restart device to finish disk migration: {err!s}",
                _LOGGER.warning,
            ) from err
