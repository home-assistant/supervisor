"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process_hostcontrol, api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_TYPE, ATTR_HOSTNAME, ATTR_FEATURES,
    ATTR_OS, ATTR_SERIAL, ATTR_INPUT, ATTR_DISK, ATTR_AUDIO, ATTR_AUDIO_INPUT,
    ATTR_AUDIO_OUTPUT, ATTR_GPIO)
from ..coresys import CoreSysAttributes
from ..validate import ALSA_CHANNEL

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})

SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_AUDIO_OUTPUT): ALSA_CHANNEL,
    vol.Optional(ATTR_AUDIO_INPUT): ALSA_CHANNEL,
})


class APIHost(CoreSysAttributes):
    """Handle rest api for host functions."""

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_TYPE: self._host_control.type,
            ATTR_VERSION: self._host_control.version,
            ATTR_LAST_VERSION: self._host_control.last_version,
            ATTR_FEATURES: self._host_control.features,
            ATTR_HOSTNAME: self._host_control.hostname,
            ATTR_OS: self._host_control.os_info,
        }

    @api_process
    async def options(self, request):
        """Process host options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_AUDIO_OUTPUT in body:
            self._config.audio_output = body[ATTR_AUDIO_OUTPUT]
        if ATTR_AUDIO_INPUT in body:
            self._config.audio_input = body[ATTR_AUDIO_INPUT]

        return True

    @api_process_hostcontrol
    def reboot(self, request):
        """Reboot host."""
        return self._host_control.reboot()

    @api_process_hostcontrol
    def shutdown(self, request):
        """Poweroff host."""
        return self._host_control.shutdown()

    @api_process_hostcontrol
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self._host_control.last_version)

        if version == self._host_control.version:
            raise RuntimeError(f"Version {version} is already in use")

        return await asyncio.shield(
            self._host_control.update(version=version), loop=self._loop)

    @api_process
    async def hardware(self, request):
        """Return local hardware infos."""
        return {
            ATTR_SERIAL: list(self._hardware.serial_devices),
            ATTR_INPUT: list(self._hardware.input_devices),
            ATTR_DISK: list(self._hardware.disk_devices),
            ATTR_GPIO: list(self._hardware.gpio_devices),
            ATTR_AUDIO: self._hardware.audio_devices,
        }
