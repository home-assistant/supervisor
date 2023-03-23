"""Home Assistant Operating-System DataDisk."""

from contextlib import suppress
from dataclasses import dataclass
import logging
from pathlib import Path

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.udisks2.block import UDisks2Block
from ..dbus.udisks2.drive import UDisks2Drive
from ..exceptions import (
    DBusError,
    DBusObjectError,
    HassOSDataDiskError,
    HassOSError,
    HassOSJobError,
    HostError,
)
from ..jobs.const import JobCondition, JobExecutionLimit
from ..jobs.decorator import Job

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(slots=True)
class Disk:
    """Representation of disk."""

    vendor: str
    model: str
    serial: str
    id: str
    size: int
    device_path: Path
    object_path: str

    @staticmethod
    def from_udisks2_drive(
        drive: UDisks2Drive, drive_block_device: UDisks2Block
    ) -> "Disk":
        """Convert UDisks2Drive into a Disk object."""
        return Disk(
            vendor=drive.vendor,
            model=drive.model,
            serial=drive.serial,
            id=drive.id or drive_block_device.device,
            size=drive.size,
            device_path=drive_block_device.device,
            object_path=drive.object_path,
        )

    @property
    def name(self) -> str:
        """Get disk name."""
        name = self.vendor
        if self.model:
            name = f"{name} {self.model}".lstrip()
        if self.serial:
            name = f"{name} ({self.serial})" if name else self.serial

        if name:
            return name

        return self.id


def _get_primary_block_device(devices: list[UDisks2Block]) -> UDisks2Block | None:
    """Return primary block device out of list or none if it cannot be determined."""
    # If there's only one block device return that
    if len(devices) == 1:
        return devices[0]

    # If there's multiple then find the (hopefully) one partition table
    partition_tables = [device for device in devices if device.partition_table]
    if len(partition_tables) == 1:
        return partition_tables[0]

    # Can't be determined if count of block devices or partition tables does not equal 1
    return None


class DataDisk(CoreSysAttributes):
    """Handle DataDisk feature from OS."""

    def __init__(self, coresys: CoreSys) -> None:
        """Initialize DataDisk."""
        self.coresys = coresys

    @property
    def disk_used(self) -> Disk | None:
        """Return current Disk for data."""
        if not self.sys_dbus.agent.datadisk.current_device:
            return None

        block_device = next(
            (
                block
                for block in self.sys_dbus.udisks2.block_devices
                if block.device == self.sys_dbus.agent.datadisk.current_device
            ),
            None,
        )
        if block_device and block_device.drive:
            with suppress(DBusObjectError):
                drive = self.sys_dbus.udisks2.get_drive(block_device.drive)
                return Disk.from_udisks2_drive(drive, block_device)

        return Disk(
            vendor="",
            model="",
            serial="",
            id=self.sys_dbus.agent.datadisk.current_device,
            size=0,
            device_path=self.sys_dbus.agent.datadisk.current_device,
            object_path="",
        )

    @property
    def available_disks(self) -> list[Disk]:
        """Return a list of possible new disk locations.

        Available disks are drives where nothing on it has been mounted
        and it can be formatted.
        """
        available: list[UDisks2Drive] = []
        for drive in self.sys_dbus.udisks2.drives:
            block_devices = self._get_block_devices_for_drive(drive)
            primary = _get_primary_block_device(block_devices)

            if primary and not any(
                block.filesystem.mount_points
                for block in block_devices
                if block.filesystem
            ):
                available.append(Disk.from_udisks2_drive(drive, primary))

        return available

    def _get_block_devices_for_drive(self, drive: UDisks2Drive) -> list[UDisks2Block]:
        """Get block devices for a drive."""
        return [
            block
            for block in self.sys_dbus.udisks2.block_devices
            if block.drive == drive.object_path
        ]

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
    async def migrate_disk(self, new_disk: str) -> None:
        """Move data partition to a new disk."""
        # Force a dbus update first so all info is up to date
        await self.sys_dbus.udisks2.update()

        try:
            target_disk: Disk = next(
                disk
                for disk in self.available_disks
                if disk.id == new_disk or disk.device_path.as_posix() == new_disk
            )
        except StopIteration:
            raise HassOSDataDiskError(
                f"'{new_disk!s}' not a valid data disk target!", _LOGGER.error
            ) from None

        # Migrate data on Host
        try:
            await self.sys_dbus.agent.datadisk.change_device(target_disk.device_path)
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
