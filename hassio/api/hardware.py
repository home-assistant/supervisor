"""Init file for HassIO hardware rest api."""
import logging

from .utils import api_process
from ..const import (
    ATTR_SERIAL, ATTR_DISK, ATTR_GPIO, ATTR_AUDIO, ATTR_INPUT, ATTR_OUTPUT)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class APIHardware(CoreSysAttributes):
    """Handle rest api for hardware functions."""

    @api_process
    async def info(self, request):
        """Show hardware info."""
        return {
            ATTR_SERIAL: list(self.sys_hardware.serial_devices),
            ATTR_INPUT: list(self.sys_hardware.input_devices),
            ATTR_DISK: list(self.sys_hardware.disk_devices),
            ATTR_GPIO: list(self.sys_hardware.gpio_devices),
            ATTR_AUDIO: self.sys_hardware.audio_devices,
        }

    @api_process
    async def audio(self, request):
        """Show ALSA audio devices."""
        return {
            ATTR_AUDIO: {
                ATTR_INPUT: self.sys_alsa.input_devices,
                ATTR_OUTPUT: self.sys_alsa.output_devices,
            }
        }
