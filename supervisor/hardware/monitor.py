"""Supervisor Hardware monitor based on udev."""
from contextlib import suppress
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional

import pyudev

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..exceptions import HardwareNotFound
from ..resolution.const import UnhealthyReason
from .const import PolicyGroup, UdevAction, UdevSubsystem
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
            self.observer = pyudev.MonitorObserver(self.monitor, self._udev_events)
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

    def _udev_events(self, action: str, kernel: pyudev.Device):
        """Incomming events from udev.

        This is inside a observe thread and need pass into our eventloop.
        """
        _LOGGER.debug("Hardware monitor: %s - %s", action, pformat(kernel))
        udev = None
        with suppress(pyudev.DeviceNotFoundAtPathError):
            udev = pyudev.Devices.from_sys_path(self.context, kernel.sys_path)

        self.sys_loop.call_soon_threadsafe(
            self._async_udev_events, action, kernel, udev
        )

    def _async_udev_events(
        self, action: str, kernel: pyudev.Device, udev: Optional[pyudev.Device]
    ):
        """Incomming events from udev into loop."""
        # Update device List
        if not kernel.device_node or self.sys_hardware.helper.hide_virtual_device(
            kernel
        ):
            return

        forward_action = None
        device = None

        ##
        # Remove
        if action in ("remove", "unbind") and udev is None:
            try:
                device = self.sys_hardware.get_by_path(Path(kernel.sys_path))
            except HardwareNotFound:
                return
            else:
                self.sys_hardware.delete_device(device)
                forward_action = UdevAction.REMOVE

        ##
        # Add
        if action in ("add", "bind") and udev is not None:
            device = Device(
                udev.sys_name,
                Path(udev.device_node),
                Path(udev.sys_path),
                udev.subsystem,
                [Path(node) for node in udev.device_links],
                {attr: udev.properties[attr] for attr in udev.properties},
            )
            self.sys_hardware.update_device(device)
            forward_action = UdevAction.ADD

        # Process Action
        if (
            device
            and forward_action
            and self.sys_core.state in (CoreState.RUNNING, CoreState.FREEZE)
        ):
            # New Sound device
            if device.subsystem == UdevSubsystem.AUDIO:
                self._action_sound(device, forward_action)

            # New serial device
            elif device.subsystem == UdevSubsystem.SERIAL:
                self._action_tty(device, forward_action)

            # New input device
            elif device.subsystem == UdevSubsystem.INPUT:
                self._action_input(device, forward_action)

            # New USB device
            elif device.subsystem == UdevSubsystem.USB:
                self._action_usb(device, forward_action)

    def _action_sound(self, device: Device, action: UdevAction):
        """Process sound actions."""
        if not self.sys_hardware.policy.is_match_cgroup(PolicyGroup.AUDIO, device):
            return
        _LOGGER.info("Detecting changed audio hardware - %s", device.path)
        self.sys_loop.call_later(2, self.sys_create_task, self.sys_host.sound.update())

    def _action_tty(self, device: Device, action: UdevAction):
        """Process tty actions."""
        if not device.by_id or not self.sys_hardware.policy.is_match_cgroup(
            PolicyGroup.UART, device
        ):
            return
        _LOGGER.info(
            "Detecting changed serial hardware %s - %s", device.path, device.by_id
        )

        # Start process TTY
        self.sys_loop.call_later(
            1,
            self.sys_create_task,
            self.sys_hardware.container.process_serial_device(device, action),
        )

    def _action_input(self, device: Device, action: UdevAction):
        """Process input actions."""
        if not device.by_id:
            return
        _LOGGER.info(
            "Detecting changed serial hardware %s - %s", device.path, device.by_id
        )

        # Start process input
        self.sys_loop.call_later(
            1,
            self.sys_create_task,
            self.sys_hardware.container.process_serial_device(device, action),
        )

    def _action_usb(self, device: Device, action: UdevAction):
        """Process usb actions."""
        if not self.sys_hardware.policy.is_match_cgroup(PolicyGroup.USB, device):
            return
        _LOGGER.info("Detecting changed usb hardware %s", device.path)

        # Start process USB
        self.sys_loop.call_later(
            1,
            self.sys_create_task,
            self.sys_hardware.container.process_usb_device(device, action),
        )
