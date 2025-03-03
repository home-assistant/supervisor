"""Read hardware info from system."""

from datetime import UTC, datetime
import logging
from pathlib import Path
import re

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
        self._last_boot: datetime | None = None

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

    async def last_boot(self) -> datetime | None:
        """Return last boot time."""
        if self._last_boot:
            return self._last_boot

        try:
            stats: str = await self.sys_run_in_executor(
                _PROC_STAT.read_text, encoding="utf-8"
            )
        except OSError as err:
            _LOGGER.error("Can't read stat data: %s", err)
            return None

        # parse stat file
        found: re.Match | None = _RE_BOOT_TIME.search(stats)
        if not found:
            _LOGGER.error("Can't found last boot time!")
            return None

        self._last_boot = datetime.fromtimestamp(int(found.group(1)), UTC)
        return self._last_boot

    def hide_virtual_device(self, udev_device: pyudev.Device) -> bool:
        """Small helper to hide not needed Devices."""
        return _RE_HIDE_SYSFS.match(udev_device.sys_path) is not None
