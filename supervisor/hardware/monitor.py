"""Supervisor Hardware monitor based on udev."""
import asyncio
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional

import pyudev

from ..const import BusEvent
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HardwareNotFound
from ..resolution.const import UnhealthyReason
from .const import HardwareAction, UdevKernelAction
from .data import Device

_LOGGER: logging.Logger = logging.getLogger(__name__)


class HwMonitor(CoreSysAttributes):
    """Hardware monitor for supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize Hardware Monitor object."""
        self.coresys: CoreSys = coresys
        self.context = pyudev.Context()
        self.monitor: Optional[pyudev.Monitor] = None
        self.observer: Optional[pyudev.MonitorObserver] = None

    async def load(self) -> None:
        """Start hardware monitor."""
        try:
            self.monitor = pyudev.Monitor.from_netlink(self.context, "kernel")
            self.monitor.set_receive_buffer_size(32 * 1024 * 1024)

            self.observer = pyudev.MonitorObserver(
                self.monitor,
                callback=lambda x: self.sys_loop.call_soon_threadsafe(
                    self._udev_events, x
                ),
            )
        except OSError:
            self.sys_resolution.unhealthy = UnhealthyReason.PRIVILEGED
            _LOGGER.critical("Not privileged to run udev monitor!")
        else:
            self.observer.start()
            _LOGGER.info("Started Supervisor hardware monitor")

    async def unload(self) -> None:
        """Shutdown sessions."""
        if self.observer is None:
            return

        self.observer.stop()
        _LOGGER.info("Stopped Supervisor hardware monitor")

    def _udev_events(self, kernel: pyudev.Device):
        """Incomming events from udev."""
        _LOGGER.debug("Hardware monitor: %s - %s", kernel.action, pformat(kernel))

        if kernel.action in (UdevKernelAction.UNBIND, UdevKernelAction.BIND):
            return
        self.sys_create_task(self._async_udev_events(kernel))

    async def _async_udev_events(self, kernel: pyudev.Device):
        """Incomming events from udev into loop."""
        # Update device List
        if not kernel.device_node or self.sys_hardware.helper.hide_virtual_device(
            kernel
        ):
            return

        hw_action: Optional[HardwareAction] = None
        device: Optional[Device] = None

        ##
        # Remove
        if kernel.action == UdevKernelAction.REMOVE:
            try:
                device = self.sys_hardware.get_by_path(Path(kernel.sys_path))
            except HardwareNotFound:
                return
            else:
                self.sys_hardware.delete_device(device)
                hw_action = HardwareAction.REMOVE

        ##
        # Add
        if kernel.action in (UdevKernelAction.ADD, UdevKernelAction.CHANGE):
            # We get pure Kernel events only inside container.
            # But udev itself need also time to initialize the device
            # before we can use it correctly
            udev = None
            for _ in range(3):
                await asyncio.sleep(2)
                try:
                    udev = pyudev.Devices.from_sys_path(self.context, kernel.sys_path)
                except pyudev.DeviceNotFoundAtPathError:
                    continue
                if udev.is_initialized:
                    break

            # Is not ready
            if not udev:
                _LOGGER.warning(
                    "Ignore device %s / failes to initialize by udev", kernel.sys_path
                )
                return

            device = Device(
                udev.sys_name,
                Path(udev.device_node),
                Path(udev.sys_path),
                udev.subsystem,
                [Path(node) for node in udev.device_links],
                {attr: udev.properties[attr] for attr in udev.properties},
            )
            self.sys_hardware.update_device(device)

            # If it's a new device - process actions
            if kernel.action == UdevKernelAction.ADD:
                hw_action = HardwareAction.ADD

        # Ignore event for future processing
        if device is None or hw_action is None:
            return
        _LOGGER.info(
            "Detecting %s hardware %s - %s", hw_action, device.path, device.by_id
        )

        # Fire Hardware event to bus
        if hw_action == HardwareAction.ADD:
            self.sys_bus.fire_event(BusEvent.HARDWARE_NEW_DEVICE, device)
        elif hw_action == HardwareAction.REMOVE:
            self.sys_bus.fire_event(BusEvent.HARDWARE_REMOVE_DEVICE, device)
