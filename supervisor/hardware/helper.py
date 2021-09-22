"""Read hardware info from system."""
from datetime import datetime
import logging
from pathlib import Path
import re
from typing import Optional

import pyudev

from ..coresys import CoreSys, CoreSysAttributes
from .const import UdevSubsystem

_LOGGER: logging.Logger = logging.getLogger(__name__)


_PROC_STAT: Path = Path("/proc/stat")
_RE_BOOT_TIME: re.Pattern = re.compile(r"btime (\d+)")

_RE_HIDE_SYSFS: re.Pattern = re.compile(r"/sys/devices/virtual/(?:tty|block|vc)/.*")


class HwHelper(CoreSysAttributes):
    """Representation of an interface to procfs, sysfs and udev."""

    def __init__(self, coresys: CoreSys):
        """Init hardware object."""
        self.coresys = coresys

    @property
    def support_audio(self) -> bool:
        """Return True if the system have audio support."""
        return bool(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.AUDIO))

    @property
    def support_gpio(self) -> bool:
        """Return True if device support GPIOs."""
        return bool(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.GPIO))

    @property
    def support_usb(self) -> bool:
        """Return True if the device have USB ports."""
        return bool(self.sys_hardware.filter_devices(subsystem=UdevSubsystem.USB))

    @property
    def last_boot(self) -> Optional[str]:
        """Return last boot time."""
        try:
            stats: str = _PROC_STAT.read_text(encoding="utf-8")
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
