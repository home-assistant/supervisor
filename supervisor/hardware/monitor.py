"""Supervisor Hardware monitor based on udev."""
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional

import pyudev

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..resolution.const import UnhealthyReason
from .const import UdevSubsystem
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

    def _udev_events(self, action: str, device: pyudev.Device):
        """Incomming events from udev.

        This is inside a observe thread and need pass into our eventloop.
        """
        _LOGGER.debug("Hardware monitor: %s - %s", action, pformat(device))
        self.sys_loop.call_soon_threadsafe(self._async_udev_events, action, device)

    def _async_udev_events(self, action: str, udev_device: pyudev.Device):
        """Incomming events from udev into loop."""
        # Update device List
        if not udev_device.device_node or self.sys_hardware.helper.hide_virtual_device(
            udev_device
        ):
            return

        device = Device(
            udev_device.sys_name,
            Path(udev_device.device_node),
            Path(udev_device.sys_path),
            udev_device.subsystem,
            [Path(node) for node in udev_device.device_links],
            {attr: udev_device.properties[attr] for attr in udev_device.properties},
        )

        # Update internal Database
        if action == "add":
            self.sys_hardware.update_device(device)
        if action == "remove":
            self.sys_hardware.delete_device(device)

        # Process device
        if self.sys_core.state in (CoreState.RUNNING, CoreState.FREEZE):
            # New Sound device
            if device.subsystem == UdevSubsystem.AUDIO and action == "add":
                self._action_sound_add(device)

            # New serial device
            if device.subsystem == UdevSubsystem.SERIAL and action == "add":
                self._action_tty_add(device)

            # New input device
            if device.subsystem == UdevSubsystem.INPUT and action == "add":
                self._action_input_add(device)

    def _action_sound_add(self, device: Device):
        """Process sound actions."""
        _LOGGER.info("Detecting changed audio hardware - %s", device.path)
        self.sys_loop.call_later(2, self.sys_create_task, self.sys_host.sound.update())

    def _action_tty_add(self, device: Device):
        """Process tty actions."""
        _LOGGER.info(
            "Detecting changed serial hardware %s - %s", device.path, device.by_id
        )
        if not device.by_id:
            return

        # Start process TTY
        self.sys_loop.call_later(
            2,
            self.sys_create_task,
            self.sys_hardware.container.process_serial_device(device),
        )

    def _action_input_add(self, device: Device):
        """Process input actions."""
        _LOGGER.info(
            "Detecting changed serial hardware %s - %s", device.path, device.by_id
        )
        if not device.by_id:
            return

        # Start process input
        self.sys_loop.call_later(
            2,
            self.sys_create_task,
            self.sys_hardware.container.process_serial_device(device),
        )
