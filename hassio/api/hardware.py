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
            ATTR_SERIAL: list(self._hardware.serial_devices),
            ATTR_INPUT: list(self._hardware.input_devices),
            ATTR_DISK: list(self._hardware.disk_devices),
            ATTR_GPIO: list(self._hardware.gpio_devices),
            ATTR_AUDIO: self._hardware.audio_devices,
        }

    @api_process
    async def audio(self, request):
        """Show ALSA audio devices."""
        return {
            ATTR_AUDIO: {
                ATTR_INPUT: self._alsa.input_devices,
                ATTR_OUTPUT: self._alsa.output_devices,
            }
        }
