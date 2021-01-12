"""Supervisor Hardware monitor based on udev."""
from datetime import timedelta
import logging
from pathlib import Path
from pprint import pformat
from typing import Optional

import pyudev

from ..const import CoreState
from ..coresys import CoreSys, CoreSysAttributes
from ..resolution.const import UnhealthyReason
from ..utils import AsyncCallFilter
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

    def _async_udev_events(self, action: str, device: pyudev.Device):
        """Incomming events from udev into loop."""
        if self.sys_core.state in (CoreState.RUNNING, CoreState.FREEZE):
            # Sound changes
            if device.subsystem == "sound":
                self._action_sound(device)

        # Update device List
        if not device.device_node:
            return

        device = Device(
            device.sys_name,
            Path(device.device_node),
            device.subsystem,
            [Path(node) for node in device.device_links],
            {attr: device.properties[attr] for attr in device.properties},
        )

        # Process the action
        if action == "add":
            self.sys_hardware.update_device(device)
        if action == "remove":
            self.sys_hardware.delete_device(device)

    @AsyncCallFilter(timedelta(seconds=5))
    def _action_sound(self, device: pyudev.Device):
        """Process sound actions."""
        _LOGGER.info("Detecting changed audio hardware")
        self.sys_loop.call_later(5, self.sys_create_task, self.sys_host.sound.update())
