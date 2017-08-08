"""Init file for HassIO host rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process_hostcontrol, api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_TYPE, ATTR_HOSTNAME, ATTR_FEATURES,
    ATTR_OS, ATTR_SERIAL, ATTR_INPUT, ATTR_DISK, ATTR_AUDIO, ATTR_OUTPUT,
    ATTR_AUDIO_INPUT, ATTR_AUDIO_OUTPUT)
from ..validate import ALSA_CHANNEL

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})

SCHEMA_OPTIONS = vol.Schema({
    vol.Optional(ATTR_AUDIO_OUTPUT): ALSA_CHANNEL,
    vol.Optional(ATTR_AUDIO_INPUT): ALSA_CHANNEL,
})


class APIHost(object):
    """Handle rest api for host functions."""

    def __init__(self, config, loop, host_control, hardware):
        """Initialize host rest api part."""
        self.config = config
        self.loop = loop
        self.host_control = host_control
        self.local_hw = hardware

    @api_process
    async def info(self, request):
        """Return host information."""
        return {
            ATTR_TYPE: self.host_control.type,
            ATTR_VERSION: self.host_control.version,
            ATTR_LAST_VERSION: self.host_control.last_version,
            ATTR_FEATURES: self.host_control.features,
            ATTR_HOSTNAME: self.host_control.hostname,
            ATTR_OS: self.host_control.os_info,
        }

    @api_process
    async def options(self, request):
        """Process host options."""
        body = await api_validate(SCHEMA_OPTIONS, request)

        if ATTR_AUDIO_OUTPUT in body:
            self.config.audio_output = body[ATTR_AUDIO_OUTPUT]

        if ATTR_AUDIO_INPUT in body:
            self.config.audio_input = body[ATTR_AUDIO_INPUT]

        return True

    @api_process_hostcontrol
    def reboot(self, request):
        """Reboot host.

        Return a coroutine.
        """
        return self.host_control.reboot()

    @api_process_hostcontrol
    def shutdown(self, request):
        """Poweroff host.

        Return a coroutine.
        """
        return self.host_control.shutdown()

    @api_process_hostcontrol
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.host_control.last_version)

        if version == self.host_control.version:
            raise RuntimeError("Version {} is already in use".format(version))

        return await asyncio.shield(
            self.host_control.update(version=version), loop=self.loop)

    @api_process
    async def hardware(self, request):
        """Return local hardware infos."""
        return {
            ATTR_SERIAL: self.local_hw.serial_devices,
            ATTR_INPUT: self.local_hw.input_devices,
            ATTR_DISK: self.local_hw.disk_devices,
            ATTR_AUDIO: self.local_hw.audio_devices,
        }
