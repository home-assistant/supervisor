"""Init file for Supervisor Audio RESTful API."""

import asyncio
from collections.abc import Awaitable
from dataclasses import asdict
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ACTIVE,
    ATTR_APPLICATION,
    ATTR_AUDIO,
    ATTR_CARD,
    ATTR_HOST,
    ATTR_INDEX,
    ATTR_INPUT,
    ATTR_NAME,
    ATTR_OUTPUT,
    ATTR_VOLUME,
)
from ..exceptions import AudioInvalidSource
from ..host.const import StreamType
from ..plugins.audio import PluginAudio
from .plugins import APIPlugin
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)


SCHEMA_VOLUME = vol.Schema(
    {
        vol.Required(ATTR_INDEX): vol.Coerce(int),
        vol.Required(ATTR_VOLUME): vol.Coerce(float),
    }
)

# pylint: disable=no-value-for-parameter
SCHEMA_MUTE = vol.Schema(
    {
        vol.Required(ATTR_INDEX): vol.Coerce(int),
        vol.Required(ATTR_ACTIVE): vol.Boolean(),
    }
)

SCHEMA_DEFAULT = vol.Schema({vol.Required(ATTR_NAME): str})

SCHEMA_PROFILE = vol.Schema(
    {vol.Required(ATTR_CARD): str, vol.Required(ATTR_NAME): str}
)

SCHEMA_STREAM_TYPE = vol.Coerce(StreamType)


def _get_stream_type(request: web.Request) -> StreamType:
    """Return validated stream type from request path."""
    source = request.match_info["source"]
    try:
        return SCHEMA_STREAM_TYPE(source)
    except vol.Invalid as err:
        raise AudioInvalidSource(source=source) from err


class APIAudio(APIPlugin[PluginAudio]):
    """Handle RESTful API for Audio functions."""

    def _info(self) -> dict[str, Any]:
        """Return Audio information."""
        return super()._info() | {
            ATTR_HOST: str(self.sys_docker.network.audio),
            ATTR_AUDIO: {
                ATTR_CARD: [asdict(card) for card in self.sys_host.sound.cards],
                ATTR_INPUT: [asdict(stream) for stream in self.sys_host.sound.inputs],
                ATTR_OUTPUT: [asdict(stream) for stream in self.sys_host.sound.outputs],
                ATTR_APPLICATION: [
                    asdict(stream) for stream in self.sys_host.sound.applications
                ],
            },
        }

    @api_process
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload Audio information."""
        return asyncio.shield(self.sys_host.sound.update())

    @api_process
    async def set_volume(self, request: web.Request) -> None:
        """Set audio volume on stream."""
        source = _get_stream_type(request)
        application: bool = request.path.endswith("application")
        body = await api_validate(SCHEMA_VOLUME, request)

        await asyncio.shield(
            self.sys_host.sound.set_volume(
                source, body[ATTR_INDEX], body[ATTR_VOLUME], application
            )
        )

    @api_process
    async def set_mute(self, request: web.Request) -> None:
        """Mute audio volume on stream."""
        source = _get_stream_type(request)
        application: bool = request.path.endswith("application")
        body = await api_validate(SCHEMA_MUTE, request)

        await asyncio.shield(
            self.sys_host.sound.set_mute(
                source, body[ATTR_INDEX], body[ATTR_ACTIVE], application
            )
        )

    @api_process
    async def set_default(self, request: web.Request) -> None:
        """Set audio default stream."""
        source = _get_stream_type(request)
        body = await api_validate(SCHEMA_DEFAULT, request)

        await asyncio.shield(self.sys_host.sound.set_default(source, body[ATTR_NAME]))

    @api_process
    async def set_profile(self, request: web.Request) -> None:
        """Set audio default sources."""
        body = await api_validate(SCHEMA_PROFILE, request)

        await asyncio.shield(
            self.sys_host.sound.ativate_profile(body[ATTR_CARD], body[ATTR_NAME])
        )
