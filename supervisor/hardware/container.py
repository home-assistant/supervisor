"""Handle udev for container."""
from contextlib import suppress
import logging
from pathlib import Path
from typing import Optional

from supervisor.const import AddonState

from ..coresys import CoreSys, CoreSysAttributes
from ..docker.interface import DockerInterface
from ..exceptions import DockerError, DockerNotFound, HardwareError
from .const import UdevSubsystem
from .data import Device

_UDEV_BY_ID = {
    UdevSubsystem.SERIAL: Path("/dev/serial/by-id"),
    UdevSubsystem.DISK: Path("/dev/disk"),
    UdevSubsystem.INPUT: Path("/dev/input/by-id"),
}

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HwContainer(CoreSysAttributes):
    """Representation of an interface to udev / container."""

    def __init__(self, coresys: CoreSys):
        """Init hardware object."""
        self.coresys = coresys

    def get_udev_id_mount(self, subystem: UdevSubsystem) -> Optional[Path]:
        """Return mount path for udev device by-id path."""
        return _UDEV_BY_ID.get(subystem)

    async def process_serial_device(self, device: Device) -> None:
        """Process a new Serial device."""
        # Add to all needed add-ons
        for addon in self.sys_addons.installed:
            if addon.state != AddonState.STARTED or addon.with_uart:
                continue
            with suppress(HardwareError):
                await self._create_device(addon.instance, device)

        # Process on Home Assistant Core
        with suppress(HardwareError):
            await self._create_device(self.sys_homeassistant.core.instance, device)

    async def process_input_device(self, device: Device) -> None:
        """Process a new Serial device."""
        # Process on Home Assistant Core
        with suppress(HardwareError):
            await self._create_device(self.sys_homeassistant.core.instance, device)

    async def _create_device(self, instance: DockerInterface, device: Device) -> None:
        """Add device into container."""
        try:
            answer = await instance.run_inside(
                f'sh -c "mknod -m 660 {device.path.as_posix()} c {device.cgroups_major} {device.cgroups_minor}"'
            )
        except DockerNotFound:
            return
        except DockerError as err:
            _LOGGER.warning("Can't add new device %s to %s", device.path, instance.name)
            raise HardwareError() from err

        if answer.exit_code == 0:
            return

        _LOGGER.warning(
            "Container response with '%s' during process %s",
            answer.output.encode(),
            device.path,
        )
