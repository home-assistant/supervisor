"""Read disk hardware info from system."""

import logging
from pathlib import Path
import shutil

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import DBusError, DBusObjectError, HardwareNotFound
from .const import UdevSubsystem
from .data import Device

_LOGGER: logging.Logger = logging.getLogger(__name__)

_MOUNTINFO: Path = Path("/proc/self/mountinfo")
_BLOCK_DEVICE_CLASS = "/sys/class/block/{}"
_BLOCK_DEVICE_EMMC_LIFE_TIME = "/sys/block/{}/device/life_time"
_DEVICE_PATH = "/dev/{}"


class HwDisk(CoreSysAttributes):
    """Representation of an interface to disk utils."""

    def __init__(self, coresys: CoreSys):
        """Init hardware object."""
        self.coresys = coresys

    def is_used_by_system(self, device: Device) -> bool:
        """Return true if this is a system partition."""
        if device.subsystem != UdevSubsystem.DISK:
            return False

        # Root
        if device.minor == 0:
            for child in device.children:
                try:
                    device = self.sys_hardware.get_by_path(child)
                except HardwareNotFound:
                    continue
                if device.subsystem == UdevSubsystem.DISK:
                    if device.attributes.get("ID_FS_LABEL", "").startswith("hassos"):
                        return True
            return False

        # Partition
        if device.minor > 0 and device.attributes.get("ID_FS_LABEL", "").startswith(
            "hassos"
        ):
            return True

        return False

    def get_disk_total_space(self, path: str | Path) -> float:
        """Return total space (GiB) on disk for path.

        Must be run in executor.
        """
        total, _, _ = shutil.disk_usage(path)
        return round(total / (1024.0**3), 1)

    def get_disk_used_space(self, path: str | Path) -> float:
        """Return used space (GiB) on disk for path.

        Must be run in executor.
        """
        _, used, _ = shutil.disk_usage(path)
        return round(used / (1024.0**3), 1)

    def get_disk_free_space(self, path: str | Path) -> float:
        """Return free space (GiB) on disk for path.

        Must be run in executor.
        """
        _, _, free = shutil.disk_usage(path)
        return round(free / (1024.0**3), 1)

    def _get_mountinfo(self, path: str) -> list[str] | None:
        mountinfo = _MOUNTINFO.read_text(encoding="utf-8")
        for line in mountinfo.splitlines():
            mountinfoarr = line.split()
            if mountinfoarr[4] == path:
                return mountinfoarr
        return None

    def _get_mount_source(self, path: str) -> str | None:
        mountinfoarr = self._get_mountinfo(path)

        if mountinfoarr is None:
            return None

        # Find optional field separator
        optionsep = 6
        while mountinfoarr[optionsep] != "-":
            optionsep += 1
        return mountinfoarr[optionsep + 2]

    def _get_mount_source_device_name(self, path: str | Path) -> str | None:
        """Get mount source device name.

        Must be run in executor.
        """
        mount_source = self._get_mount_source(str(path))
        if not mount_source or mount_source == "overlay":
            return None

        mount_source_path = Path(mount_source)
        if not mount_source_path.is_block_device():
            return None

        # This looks a bit funky but it is more or less what lsblk is doing to get
        # the parent dev reliably

        # Get class device...
        mount_source_device_part = Path(
            _BLOCK_DEVICE_CLASS.format(mount_source_path.name)
        )

        # ... resolve symlink and get parent device from that path.
        return mount_source_device_part.resolve().parts[-2]

    async def _try_get_nvme_lifetime(self, device_name: str) -> float | None:
        """Get NVMe device lifetime."""
        device_path = Path(_DEVICE_PATH.format(device_name))
        try:
            block_device = self.sys_dbus.udisks2.get_block_device_by_path(device_path)
            drive = self.sys_dbus.udisks2.get_drive(block_device.drive)
        except DBusObjectError:
            _LOGGER.warning(
                "Unable to find UDisks2 drive for device at %s", device_path.as_posix()
            )
            return None

        # Exit if this isn't an NVMe device
        if not drive.nvme_controller:
            return None

        try:
            smart_log = await drive.nvme_controller.smart_get_attributes()
        except DBusError as err:
            _LOGGER.warning(
                "Unable to get smart log for drive %s due to %s", drive.id, err
            )
            return None

        # UDisks2 documentation specifies that value can exceed 100
        if smart_log.percent_used >= 100:
            _LOGGER.warning(
                "NVMe controller reports that its estimated life-time has been exceeded!"
            )
            return 100.0
        return smart_log.percent_used

    def _try_get_emmc_life_time(self, device_name: str) -> float | None:
        """Get eMMC life_time.

        Must be run in executor.
        """
        life_time_path = Path(_BLOCK_DEVICE_EMMC_LIFE_TIME.format(device_name))

        if not life_time_path.exists():
            return None

        # JEDEC health status DEVICE_LIFE_TIME_EST_TYP_A/B
        emmc_life_time = life_time_path.read_text(encoding="utf-8").split()

        if len(emmc_life_time) < 2:
            return None

        # Type B life time estimate represents the user partition.
        life_time_value = int(emmc_life_time[1], 16)

        # 0=Not defined, 1-10=0-100% device life time used, 11=Exceeded
        if life_time_value == 0:
            return None

        if life_time_value == 11:
            logging.warning(
                "eMMC reports that its estimated life-time has been exceeded!"
            )
            return 100.0

        # Return the optimistic estimate (0x02 -> 10%-20%, return 10%)
        return (life_time_value - 1) * 10.0

    async def get_disk_life_time(self, path: str | Path) -> float | None:
        """Return life time estimate of the underlying SSD drive."""
        mount_source_device_name = await self.sys_run_in_executor(
            self._get_mount_source_device_name, path
        )
        if mount_source_device_name is None:
            return None

        # First check if its an NVMe device and get lifetime information that way
        nvme_lifetime = await self._try_get_nvme_lifetime(mount_source_device_name)
        if nvme_lifetime is not None:
            return nvme_lifetime

        # Else try to get lifetime information for eMMC devices. Other types of devices will return None
        return await self.sys_run_in_executor(
            self._try_get_emmc_life_time, mount_source_device_name
        )
