"""Supervisor Hardware monitor based on udev."""
import asyncio
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional

import pyudev

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HardwareNotFound
from ..resolution.const import UnhealthyReason
from .const import HardwareAction, PolicyGroup, UdevKernelAction, UdevSubsystem
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

        try:
            # We get pure Kernel events only inside container.
            # But udev itself need also time to initialize the device
            # before we can use it correctly
            while True:
                await asyncio.sleep(2)
                udev = pyudev.Devices.from_sys_path(self.context, kernel.sys_path)
                if udev.is_initialized:
                    break
        except pyudev.DeviceNotFoundAtPathError:
            udev = None

        hw_action = None
        device = None

        ##
        # Remove
        if kernel.action == UdevKernelAction.REMOVE and udev is None:
            try:
                device = self.sys_hardware.get_by_path(Path(kernel.sys_path))
            except HardwareNotFound:
                return
            else:
                self.sys_hardware.delete_device(device)
                hw_action = HardwareAction.REMOVE

        ##
        # Add
        if kernel.action == UdevKernelAction.ADD and udev is not None:
            device = Device(
                udev.sys_name,
                Path(udev.device_node),
                Path(udev.sys_path),
                udev.subsystem,
                [Path(node) for node in udev.device_links],
                {attr: udev.properties[attr] for attr in udev.properties},
            )
            self.sys_hardware.update_device(device)
            hw_action = HardwareAction.ADD

        # Process Action
        if (
            device
            and hw_action
            and self.sys_core.state in (CoreState.RUNNING, CoreState.FREEZE)
        ):
            # New Sound device
            if device.subsystem == UdevSubsystem.AUDIO:
                await self._action_sound(device, hw_action)

            # serial device
            elif device.subsystem == UdevSubsystem.SERIAL:
                await self._action_tty(device, hw_action)

            # input device
            elif device.subsystem == UdevSubsystem.INPUT:
                await self._action_input(device, hw_action)

            # USB device
            elif device.subsystem == UdevSubsystem.USB:
                await self._action_usb(device, hw_action)

            # GPIO device
            elif device.subsystem == UdevSubsystem.GPIO:
                await self._action_gpio(device, hw_action)

    async def _action_sound(self, device: Device, action: HardwareAction):
        """Process sound actions."""
        if not self.sys_hardware.policy.is_match_cgroup(PolicyGroup.AUDIO, device):
            return
        _LOGGER.info("Detecting %s audio hardware - %s", action, device.path)
        await self.sys_create_task(self.sys_host.sound.update())

    async def _action_tty(self, device: Device, action: HardwareAction):
        """Process tty actions."""
        if not device.by_id or not self.sys_hardware.policy.is_match_cgroup(
            PolicyGroup.UART, device
        ):
            return
        _LOGGER.info(
            "Detecting %s serial hardware %s - %s", action, device.path, device.by_id
        )

    async def _action_input(self, device: Device, action: HardwareAction):
        """Process input actions."""
        if not device.by_id:
            return
        _LOGGER.info(
            "Detecting %s serial hardware %s - %s", action, device.path, device.by_id
        )

    async def _action_usb(self, device: Device, action: HardwareAction):
        """Process usb actions."""
        if not self.sys_hardware.policy.is_match_cgroup(PolicyGroup.USB, device):
            return
        _LOGGER.info("Detecting %s usb hardware %s", action, device.path)

    async def _action_gpio(self, device: Device, action: HardwareAction):
        """Process gpio actions."""
        if not self.sys_hardware.policy.is_match_cgroup(PolicyGroup.GPIO, device):
            return
        _LOGGER.info("Detecting %s GPIO hardware %s", action, device.path)
