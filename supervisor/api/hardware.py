"""Init file for Supervisor hardware RESTful API."""
import logging
from typing import Any, Awaitable, Dict

from aiohttp import web

from ..const import ATTR_AUDIO, ATTR_DEVICES, ATTR_INPUT, ATTR_NAME, ATTR_OUTPUT
from ..coresys import CoreSysAttributes
from ..hardware.const import (
    ATTR_ATTRIBUTES,
    ATTR_BY_ID,
    ATTR_DEV_PATH,
    ATTR_SUBSYSTEM,
    ATTR_SYSFS,
)
from ..hardware.data import Device
from .utils import api_process

_LOGGER: logging.Logger = logging.getLogger(__name__)


def device_struct(device: Device) -> Dict[str, Any]:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_NAME: device.name,
        ATTR_SYSFS: device.sysfs,
        ATTR_DEV_PATH: device.path,
        ATTR_SUBSYSTEM: device.subsystem,
        ATTR_BY_ID: device.by_id,
        ATTR_ATTRIBUTES: device.attributes,
    }


class APIHardware(CoreSysAttributes):
    """Handle RESTful API for hardware functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Show hardware info."""
        return {
            ATTR_DEVICES: [
                device_struct(device) for device in self.sys_hardware.devices
            ]
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
        _LOGGER.debug("Ignoring DEPRECATED hardware trigger function call.")
