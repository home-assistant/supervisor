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

_RE_HIDE_SYSFS: re.Pattern = re.compile(r"/sys/devices/virtual/(?:tty|block)/.*")


class HwHelper(CoreSysAttributes):
    """Representation of an interface to procfs, sysfs and udev."""

    def __init__(self, coresys: CoreSys):
        """Init hardware object."""
        self.coresys = coresys

    @property
    def support_audio(self) -> bool:
        """Return True if the system have audio support."""
        return len(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.AUDIO)) > 0

    @property
    def support_gpio(self) -> bool:
        """Return True if device support GPIOs."""
        return len(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.GPIO)) > 0

    @property
    def support_usb(self) -> bool:
        """Return True if the device have USB ports."""
        return len(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.USB)) > 0

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
