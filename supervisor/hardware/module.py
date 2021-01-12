"""Hardware Manager of Supervisor."""
import logging
from pathlib import Path
from typing import Dict, List

import pyudev

from ..coresys import CoreSys, CoreSysAttributes
from .data import Device
from .helper import HwHelper
from .monitor import HwMonitor

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HardwareManager(CoreSysAttributes):
    """Hardware manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Hardware Monitor object."""
        self.coresys: CoreSys = coresys
        self._devices: Dict[str, Device] = {}
        self._udev = pyudev.Context()

        self._montior: HwMonitor = HwMonitor(coresys)
        self._helper: HwHelper = HwHelper(coresys)

    @property
    def monitor(self) -> HwMonitor:
        """Return Hardware Monitor instance."""
        return self._montior

    @property
    def helper(self) -> HwHelper:
        """Return Hardware Helper instance."""
        return self._helper

    @property
    def devices(self) -> List[Device]:
        """Return List of devices."""
        return list(self._devices.values())

    def update_device(self, device: Device) -> None:
        """Update or add a (new) Device."""
        self._devices[device.name] = Device

    def delete_device(self, device: Device) -> None:
        """Remove a device from the list."""
        self._devices.pop(device.name, None)

    def exists_device(self, device_node: Path) -> bool:
        """Check if device exists on Host."""
        for device in self.devices:
            if device_node == device.path:
                return True
            if device_node in device.links:
                return True
        return False

    def _import_fresh(self) -> None:
        """Import fresh from udev database."""
        self._devices.clear()

        # Exctract all devices
        for device in self._udev.list_devices():
            # Skip devices without mapping
            if not device.device_node:
                continue

            self._devices[device.sys_name] = Device(
                device.sys_name,
                Path(device.device_node),
                device.subsystem,
                [Path(node) for node in device.device_links],
                {attr: device.properties[attr] for attr in device.properties},
            )

    async def load(self) -> None:
        """Load hardware backend."""
        self._import_fresh()
        await self.monitor.load()

    async def unload(self) -> None:
        """Shutdown sessions."""
        await self.monitor.unload()
