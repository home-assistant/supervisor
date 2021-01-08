"""Read hardware info from system."""
from datetime import datetime
import logging
from pathlib import Path
import re
import shutil
from typing import Optional, Union

import pyudev

from ..coresys import CoreSys, CoreSysAttributes
from .const import UdevSubsystem

_LOGGER: logging.Logger = logging.getLogger(__name__)


_PROC_STAT: Path = Path("/proc/stat")
_RE_BOOT_TIME: re.Pattern = re.compile(r"btime (\d+)")

_GPIO_DEVICES: Path = Path("/sys/class/gpio")
_SOC_DEVICES: Path = Path("/sys/devices/platform/soc")

_RE_HIDE_SYSFS: re.Pattern = re.compile(r"/sys/devices/virtual/(?:tty|block)/.*")

_MOUNTINFO: Path = Path("/proc/self/mountinfo")
_BLOCK_DEVICE_CLASS = "/sys/class/block/{}"
_BLOCK_DEVICE_EMMC_LIFE_TIME = "/sys/block/{}/device/life_time"


class HwHelper(CoreSysAttributes):
    """Representation of an interface to procfs, sysfs and udev."""

    def __init__(self, coresys: CoreSys):
        """Init hardware object."""
        self.coresys = coresys

    @property
    def support_audio(self) -> bool:
        """Return True if the system have audio support."""
        return len(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.AUDIO))

    @property
    def support_gpio(self) -> bool:
        """Return True if device support GPIOs."""
        return _SOC_DEVICES.exists() and _GPIO_DEVICES.exists()

    @property
    def last_boot(self) -> Optional[str]:
        """Return last boot time."""
        try:
            with _PROC_STAT.open("r") as stat_file:
                stats: str = stat_file.read()
        except OSError as err:
            _LOGGER.error("Can't read stat data: %s", err)
            return None

        # parse stat file
        found: Optional[re.Match] = _RE_BOOT_TIME.search(stats)
        if not found:
            _LOGGER.error("Can't found last boot time!")
            return None

        return datetime.utcfromtimestamp(int(found.group(1)))

    def hide_virtual_device(self, udev_device: pyudev.Device) -> bool:
        """Small helper to hide not needed Devices."""
        return _RE_HIDE_SYSFS.match(udev_device.sys_path) is not None

    def get_disk_total_space(self, path: Union[str, Path]) -> float:
        """Return total space (GiB) on disk for path."""
        total, _, _ = shutil.disk_usage(path)
        return round(total / (1024.0 ** 3), 1)

    def get_disk_used_space(self, path: Union[str, Path]) -> float:
        """Return used space (GiB) on disk for path."""
        _, used, _ = shutil.disk_usage(path)
        return round(used / (1024.0 ** 3), 1)

    def get_disk_free_space(self, path: Union[str, Path]) -> float:
        """Return free space (GiB) on disk for path."""
        _, _, free = shutil.disk_usage(path)
        return round(free / (1024.0 ** 3), 1)

    def _get_mountinfo(self, path: str) -> str:
        mountinfo = _MOUNTINFO.read_text()
        for line in mountinfo.splitlines():
            mountinfoarr = line.split()
            if mountinfoarr[4] == path:
                return mountinfoarr
        return None

    def _get_mount_source(self, path: str) -> str:
        mountinfoarr = self._get_mountinfo(path)

        if mountinfoarr is None:
            return None

        # Find optional field separator
        optionsep = 6
        while mountinfoarr[optionsep] != "-":
            optionsep += 1
        return mountinfoarr[optionsep + 2]

    def _try_get_emmc_life_time(self, device_name: str) -> float:
        # Get eMMC life_time
        life_time_path = Path(_BLOCK_DEVICE_EMMC_LIFE_TIME.format(device_name))

        if not life_time_path.exists():
            return None

        # JEDEC health status DEVICE_LIFE_TIME_EST_TYP_A/B
        emmc_life_time = life_time_path.read_text().split()

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

        # Return the pessimistic estimate (0x02 -> 10%-20%, return 20%)
        return life_time_value * 10.0

    def get_disk_ssd_life_time(self, path: Union[str, Path]) -> float:
        """Return life time estimate of the underlying SSD drive."""
        mount_source = self._get_mount_source(str(path))
        if mount_source == "overlay":
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
        mount_source_device_name = mount_source_device_part.resolve().parts[-2]

        # Currently only eMMC block devices supported
        return self._try_get_emmc_life_time(mount_source_device_name)
