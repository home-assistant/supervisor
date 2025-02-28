"""Home Assistant Operating-System DataDisk."""

import asyncio
from contextlib import suppress
from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any, Final

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys, CoreSysAttributes
from ..dbus.const import DBUS_ATTR_ID_LABEL, DBUS_IFACE_BLOCK
from ..dbus.udisks2.block import UDisks2Block
from ..dbus.udisks2.const import FormatType
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
from ..resolution.checks.disabled_data_disk import CheckDisabledDataDisk
from ..resolution.checks.multiple_data_disks import CheckMultipleDataDisks
from ..utils.sentry import async_capture_exception
from .const import (
    FILESYSTEM_LABEL_DATA_DISK,
    FILESYSTEM_LABEL_DISABLED_DATA_DISK,
    PARTITION_NAME_EXTERNAL_DATA_DISK,
    PARTITION_NAME_OLD_EXTERNAL_DATA_DISK,
)

LINUX_DATA_PARTITION_GUID: Final = "0FC63DAF-8483-4772-8E79-3D69D8477DE4"
OS_AGENT_MARK_DATA_MOVE_VERSION: Final = AwesomeVersion("1.5.0")

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
    device_object_path: str

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
            device_object_path=drive_block_device.object_path,
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
            id=self.sys_dbus.agent.datadisk.current_device.as_posix(),
            size=0,
            device_path=self.sys_dbus.agent.datadisk.current_device.as_posix(),
            object_path="",
            device_object_path="",
        )

    @property
    def disk_used_id(self) -> str | None:
        """Return current Disk id for data."""
        disk_used = self.disk_used
        return disk_used.id if disk_used else None

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

    @property
    def check_multiple_data_disks(self) -> CheckMultipleDataDisks:
        """Resolution center check for multiple data disks."""
        return self.sys_resolution.check.get("multiple_data_disks")

    @property
    def check_disabled_data_disk(self) -> CheckDisabledDataDisk:
        """Resolution center check for disabled data disk."""
        return self.sys_resolution.check.get("disabled_data_disk")

    def _get_block_devices_for_drive(self, drive: UDisks2Drive) -> list[UDisks2Block]:
        """Get block devices for a drive."""
        return [
            block
            for block in self.sys_dbus.udisks2.block_devices
            if block.drive == drive.object_path
        ]

    @Job(name="data_disk_load", conditions=[JobCondition.OS_AGENT], internal=True)
    async def load(self) -> None:
        """Load DataDisk feature."""
        # Update datadisk details on OS-Agent
        if self.sys_dbus.agent.version >= AwesomeVersion("1.2.0"):
            await self.sys_dbus.agent.datadisk.reload_device()

        # Register for signals on devices added/removed
        if self.sys_dbus.udisks2.is_connected:
            self.sys_dbus.udisks2.udisks2_object_manager.dbus.object_manager.on_interfaces_added(
                self._udisks2_interface_added
            )
            self.sys_dbus.udisks2.udisks2_object_manager.dbus.object_manager.on_interfaces_removed(
                self._udisks2_interface_removed
            )

    @Job(
        name="data_disk_migrate",
        conditions=[JobCondition.HAOS, JobCondition.OS_AGENT, JobCondition.HEALTHY],
        limit=JobExecutionLimit.ONCE,
        on_condition=HassOSJobError,
    )
    async def migrate_disk(self, new_disk: str) -> None:
        """Move data partition to a new disk."""
        # Force a dbus update first so all info is up to date
        await self.sys_dbus.udisks2.update()

        target_disk: list[Disk] = [
            disk
            for disk in self.available_disks
            if disk.id == new_disk or disk.device_path.as_posix() == new_disk
        ]
        if len(target_disk) != 1:
            raise HassOSDataDiskError(
                f"'{new_disk}' not a valid data disk target!", _LOGGER.error
            ) from None

        # If any other partition is named "hassos-data-external" error and ask for its removal
        # otherwise it will create a race condition at startup
        if self.disk_used and (
            conflicts := [
                block
                for block in self.sys_dbus.udisks2.block_devices
                if block.partition
                and block.partition.name_ == PARTITION_NAME_EXTERNAL_DATA_DISK
                and block.device != self.disk_used.device_path
                and block.drive != target_disk[0].object_path
            ]
        ):
            raise HassOSDataDiskError(
                f"Partition(s) {', '.join([conflict.device.as_posix() for conflict in conflicts])} have name 'hassos-data-external' which prevents migration. Remove or rename them first.",
                _LOGGER.error,
            )

        # Older OS did not have mark data move API. Must let OS do disk format & migration
        if self.sys_dbus.agent.version < OS_AGENT_MARK_DATA_MOVE_VERSION:
            try:
                await self.sys_dbus.agent.datadisk.change_device(
                    target_disk[0].device_path
                )
            except DBusError as err:
                raise HassOSDataDiskError(
                    f"Can't move data partition to {new_disk!s}: {err!s}", _LOGGER.error
                ) from err
        else:
            # Format disk then tell OS to migrate next reboot
            current_block = (
                self.sys_dbus.udisks2.get_block_device(
                    self.disk_used.device_object_path
                )
                if self.disk_used
                else None
            )

            # If migrating from one external data disk to another, rename the old one to prevent conflicts
            # Do this first because otherwise a subsequent failure could create a race condition on reboot
            if (
                current_block
                and current_block.partition
                and current_block.partition.name_ == PARTITION_NAME_EXTERNAL_DATA_DISK
            ):
                try:
                    await current_block.partition.set_name(
                        PARTITION_NAME_OLD_EXTERNAL_DATA_DISK
                    )
                except DBusError as err:
                    raise HassOSDataDiskError(
                        f"Could not rename existing external data disk to prevent name conflict: {err!s}",
                        _LOGGER.error,
                    ) from err

            partition = await self._format_device_with_single_partition(target_disk[0])

            if current_block and current_block.size > partition.size:
                raise HassOSDataDiskError(
                    f"Cannot use {new_disk} as data disk as it is smaller then the current one (new: {partition.size}, current: {current_block.size})",
                    _LOGGER.error,
                )

            try:
                await self.sys_dbus.agent.datadisk.mark_data_move()
            except DBusError as err:
                raise HassOSDataDiskError(
                    f"Unable to create data disk migration marker: {err!s}",
                    _LOGGER.error,
                ) from err

        # Restart Host for finish the process
        try:
            await self.sys_host.control.reboot()
        except HostError as err:
            raise HassOSError(
                f"Can't restart device to finish disk migration: {err!s}",
                _LOGGER.warning,
            ) from err

    @Job(
        name="data_disk_wipe",
        conditions=[JobCondition.HAOS, JobCondition.OS_AGENT, JobCondition.HEALTHY],
        limit=JobExecutionLimit.ONCE,
        on_condition=HassOSJobError,
    )
    async def wipe_disk(self) -> None:
        """Wipe the current data disk."""
        _LOGGER.info("Scheduling wipe of data disk on next reboot")
        try:
            if not await self.sys_dbus.agent.system.schedule_wipe_device():
                raise HassOSDataDiskError(
                    "Can't schedule wipe of data disk, check host logs for details",
                    _LOGGER.error,
                )
        except DBusError as err:
            raise HassOSDataDiskError(
                f"Can't schedule wipe of data disk: {err!s}", _LOGGER.error
            ) from err

        _LOGGER.info("Rebooting the host to finish the wipe")
        try:
            await self.sys_host.control.reboot()
        except (HostError, DBusError) as err:
            raise HassOSError(
                f"Can't restart device to finish data disk wipe: {err!s}",
                _LOGGER.warning,
            ) from err

    async def _format_device_with_single_partition(
        self, new_disk: Disk
    ) -> UDisks2Block:
        """Format device with a single partition to use as data disk."""
        block_device: UDisks2Block = self.sys_dbus.udisks2.get_block_device(
            new_disk.device_object_path
        )

        try:
            await block_device.format(FormatType.GPT)
        except DBusError as err:
            await async_capture_exception(err)
            raise HassOSDataDiskError(
                f"Could not format {new_disk.id}: {err!s}", _LOGGER.error
            ) from err

        await block_device.check_type()
        if not block_device.partition_table:
            raise HassOSDataDiskError(
                "Block device does not contain a partition table after format, cannot create data partition",
                _LOGGER.error,
            )

        try:
            partition = await block_device.partition_table.create_partition(
                0, 0, LINUX_DATA_PARTITION_GUID, PARTITION_NAME_EXTERNAL_DATA_DISK
            )
        except DBusError as err:
            await async_capture_exception(err)
            raise HassOSDataDiskError(
                f"Could not create new data partition: {err!s}", _LOGGER.error
            ) from err

        try:
            partition_block = await UDisks2Block.new(
                partition, self.sys_dbus.bus, sync_properties=False
            )
        except DBusError as err:
            raise HassOSDataDiskError(
                f"New data partition at {partition} is missing or unusable",
                _LOGGER.error,
            ) from err

        _LOGGER.debug(
            "New data partition prepared on device %s", partition_block.device
        )
        return partition_block

    async def _udisks2_interface_added(
        self, _: str, properties: dict[str, dict[str, Any]]
    ):
        """If a data disk is added, trigger the resolution check."""
        if (
            DBUS_IFACE_BLOCK not in properties
            or DBUS_ATTR_ID_LABEL not in properties[DBUS_IFACE_BLOCK]
        ):
            return

        if (
            properties[DBUS_IFACE_BLOCK][DBUS_ATTR_ID_LABEL]
            == FILESYSTEM_LABEL_DATA_DISK
        ):
            check = self.check_multiple_data_disks
        elif (
            properties[DBUS_IFACE_BLOCK][DBUS_ATTR_ID_LABEL]
            == FILESYSTEM_LABEL_DISABLED_DATA_DISK
        ):
            check = self.check_disabled_data_disk
        else:
            return

        # Delay briefly before running check to allow data updates to occur
        await asyncio.sleep(0.1)
        await check()

    async def _udisks2_interface_removed(self, _: str, interfaces: list[str]):
        """If affected by a data disk issue, re-check on removal of a block device."""
        if DBUS_IFACE_BLOCK not in interfaces:
            return

        if any(
            issue.type == self.check_multiple_data_disks.issue
            and issue.context == self.check_multiple_data_disks.context
            for issue in self.sys_resolution.issues
        ):
            check = self.check_multiple_data_disks
        elif any(
            issue.type == self.check_disabled_data_disk.issue
            and issue.context == self.check_disabled_data_disk.context
            for issue in self.sys_resolution.issues
        ):
            check = self.check_disabled_data_disk
        else:
            return

        # Delay briefly before running check to allow data updates to occur
        await asyncio.sleep(0.1)
        await check()
