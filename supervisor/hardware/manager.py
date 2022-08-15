"""Hardware Manager of Supervisor."""
import logging
from pathlib import Path

import pyudev

from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HardwareNotFound
from .const import UdevSubsystem
from .data import Device
from .disk import HwDisk
from .helper import HwHelper
from .monitor import HwMonitor
from .policy import HwPolicy

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HardwareManager(CoreSysAttributes):
    """Hardware manager for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Hardware Monitor object."""
        self.coresys: CoreSys = coresys
        self._devices: dict[str, Device] = {}
        self._udev = pyudev.Context()

        self._montior: HwMonitor = HwMonitor(coresys)
        self._helper: HwHelper = HwHelper(coresys)
        self._policy: HwPolicy = HwPolicy(coresys)
        self._disk: HwDisk = HwDisk(coresys)

    @property
    def monitor(self) -> HwMonitor:
        """Return Hardware Monitor instance."""
        return self._montior

    @property
    def helper(self) -> HwHelper:
        """Return Hardware Helper instance."""
        return self._helper

    @property
    def policy(self) -> HwPolicy:
        """Return Hardware policy instance."""
        return self._policy

    @property
    def disk(self) -> HwDisk:
        """Return Hardware disk instance."""
        return self._disk

    @property
    def devices(self) -> list[Device]:
        """Return List of devices."""
        return list(self._devices.values())

    def get_by_path(self, device_node: Path) -> Device:
        """Get Device by path."""
        for device in self.devices:
            if device_node in (device.path, device.sysfs):
                return device
            if device_node in device.links:
                return device
        raise HardwareNotFound()

    def filter_devices(self, subsystem: UdevSubsystem | None = None) -> list[Device]:
        """Return a filtered list."""
        devices = set()
        for device in self.devices:
            if subsystem and device.subsystem != subsystem:
                continue
            devices.add(device)
        return list(devices)

    def update_device(self, device: Device) -> None:
        """Update or add a (new) Device."""
        self._devices[device.name] = device

    def delete_device(self, device: Device) -> None:
        """Remove a device from the list."""
        self._devices.pop(device.name, None)

    def exists_device_node(self, device_node: Path) -> bool:
        """Check if device exists on Host."""
        try:
            self.get_by_path(device_node)
        except HardwareNotFound:
            return False
        return True

    def check_subsystem_parents(self, device: Device, subsystem: UdevSubsystem) -> bool:
        """Return True if the device is part of the given subsystem parent."""
        udev_device: pyudev.Device = pyudev.Devices.from_sys_path(
            self._udev, str(device.sysfs)
        )
        return udev_device.find_parent(subsystem.value) is not None

    def _import_devices(self) -> None:
        """Import fresh from udev database."""
        self._devices.clear()

        # Exctract all devices
        for device in self._udev.list_devices():
            # Skip devices without mapping
            if not device.device_node or self.helper.hide_virtual_device(device):
                continue
            self._devices[device.sys_name] = Device.import_udev(device)

    async def load(self) -> None:
        """Load hardware backend."""
        self._import_devices()
        await self.monitor.load()

    async def unload(self) -> None:
        """Shutdown sessions."""
        await self.monitor.unload()
