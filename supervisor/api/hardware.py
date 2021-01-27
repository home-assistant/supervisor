"""Init file for Supervisor hardware RESTful API."""
import logging
from typing import Any, Awaitable, Dict, List

from aiohttp import web
import attr

from ..const import (
    ATTR_AUDIO,
    ATTR_DEVICES,
    ATTR_DISK,
    ATTR_GPIO,
    ATTR_INPUT,
    ATTR_OUTPUT,
    ATTR_SERIAL,
    ATTR_USB,
)
from ..coresys import CoreSysAttributes
from .utils import api_process

_LOGGER: logging.Logger = logging.getLogger(__name__)


class APIHardware(CoreSysAttributes):
    """Handle RESTful API for hardware functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Show hardware info."""
        serial: List[str] = []

        # Create Serial list with device links
        for device in self.sys_hardware.helper.serial_devices:
            serial.append(device.path.as_posix())
            for link in device.links:
                if not link.match("/dev/serial/by-id/*"):
                    continue
                serial.append(link.as_posix())

        return {
            ATTR_DEVICES: [attr.asdict(device) for device in self.sys_hardware.devices],
            ATTR_SERIAL: serial,
            ATTR_INPUT: list(self.sys_hardware.helper.input_devices),
            ATTR_DISK: [
                device.path.as_posix()
                for device in self.sys_hardware.helper.disk_devices
            ],
            ATTR_GPIO: list(self.sys_hardware.helper.gpio_devices),
            ATTR_USB: [
                device.path.as_posix()
                for device in self.sys_hardware.helper.usb_devices
            ],
            ATTR_AUDIO: self.sys_hardware.helper.audio_devices,
        }

    @api_process
    async def audio(self, request: web.Request) -> Dict[str, Any]:
        """Show pulse audio profiles."""
        return {
            ATTR_AUDIO: {
                ATTR_INPUT: {
                    profile.name: profile.description
                    for profile in self.sys_host.sound.inputs
                },
                ATTR_OUTPUT: {
                    profile.name: profile.description
                    for profile in self.sys_host.sound.outputs
                },
            }
        }

    @api_process
    async def trigger(self, request: web.Request) -> Awaitable[None]:
        """Trigger a udev device reload."""
        _LOGGER.warning("DEPRICATED hardware trigger function called")
