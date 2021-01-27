"""Init file for Supervisor hardware RESTful API."""
import logging
from typing import Any, Awaitable, Dict

from aiohttp import web
import attr

from ..const import ATTR_AUDIO, ATTR_DEVICES, ATTR_INPUT, ATTR_OUTPUT
from ..coresys import CoreSysAttributes
from .utils import api_process

_LOGGER: logging.Logger = logging.getLogger(__name__)


class APIHardware(CoreSysAttributes):
    """Handle RESTful API for hardware functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Show hardware info."""
        return {
            ATTR_DEVICES: [attr.asdict(device) for device in self.sys_hardware.devices]
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
