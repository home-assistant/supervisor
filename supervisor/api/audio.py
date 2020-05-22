"""Init file for Supervisor Audio RESTful API."""
import asyncio
import logging
from typing import Any, Awaitable, Dict

from aiohttp import web
import attr
import voluptuous as vol

from ..const import (
    ATTR_ACTIVE,
    ATTR_APPLICATION,
    ATTR_AUDIO,
    ATTR_BLK_READ,
    ATTR_BLK_WRITE,
    ATTR_CARD,
    ATTR_CPU_PERCENT,
    ATTR_HOST,
    ATTR_INDEX,
    ATTR_INPUT,
    ATTR_MEMORY_LIMIT,
    ATTR_MEMORY_PERCENT,
    ATTR_MEMORY_USAGE,
    ATTR_NAME,
    ATTR_NETWORK_RX,
    ATTR_NETWORK_TX,
    ATTR_OUTPUT,
    ATTR_VERSION,
    ATTR_VERSION_LATEST,
    ATTR_VOLUME,
    CONTENT_TYPE_BINARY,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..host.sound import StreamType
from ..validate import simple_version
from .utils import api_process, api_process_raw, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({vol.Optional(ATTR_VERSION): simple_version})

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

SCHEMA_DEFAULT = vol.Schema({vol.Required(ATTR_NAME): vol.Coerce(str)})

SCHEMA_PROFILE = vol.Schema(
    {vol.Required(ATTR_CARD): vol.Coerce(str), vol.Required(ATTR_NAME): vol.Coerce(str)}
)


class APIAudio(CoreSysAttributes):
    """Handle RESTful API for Audio functions."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return Audio information."""
        return {
            ATTR_VERSION: self.sys_plugins.audio.version,
            ATTR_VERSION_LATEST: self.sys_plugins.audio.latest_version,
            ATTR_HOST: str(self.sys_docker.network.audio),
            ATTR_AUDIO: {
                ATTR_CARD: [attr.asdict(card) for card in self.sys_host.sound.cards],
                ATTR_INPUT: [
                    attr.asdict(stream) for stream in self.sys_host.sound.inputs
                ],
                ATTR_OUTPUT: [
                    attr.asdict(stream) for stream in self.sys_host.sound.outputs
                ],
                ATTR_APPLICATION: [
                    attr.asdict(stream) for stream in self.sys_host.sound.applications
                ],
            },
        }

    @api_process
    async def stats(self, request: web.Request) -> Dict[str, Any]:
        """Return resource information."""
        stats = await self.sys_plugins.audio.stats()

        return {
            ATTR_CPU_PERCENT: stats.cpu_percent,
            ATTR_MEMORY_USAGE: stats.memory_usage,
            ATTR_MEMORY_LIMIT: stats.memory_limit,
            ATTR_MEMORY_PERCENT: stats.memory_percent,
            ATTR_NETWORK_RX: stats.network_rx,
            ATTR_NETWORK_TX: stats.network_tx,
            ATTR_BLK_READ: stats.blk_read,
            ATTR_BLK_WRITE: stats.blk_write,
        }

    @api_process
    async def update(self, request: web.Request) -> None:
        """Update Audio plugin."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.sys_plugins.audio.latest_version)

        if version == self.sys_plugins.audio.version:
            raise APIError(f"Version {version} is already in use")
        await asyncio.shield(self.sys_plugins.audio.update(version))

    @api_process_raw(CONTENT_TYPE_BINARY)
    def logs(self, request: web.Request) -> Awaitable[bytes]:
        """Return Audio Docker logs."""
        return self.sys_plugins.audio.logs()

    @api_process
    def restart(self, request: web.Request) -> Awaitable[None]:
        """Restart Audio plugin."""
        return asyncio.shield(self.sys_plugins.audio.restart())

    @api_process
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload Audio information."""
        return asyncio.shield(self.sys_host.sound.update())

    @api_process
    async def set_volume(self, request: web.Request) -> None:
        """Set audio volume on stream."""
        source: StreamType = StreamType(request.match_info.get("source"))
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
        source: StreamType = StreamType(request.match_info.get("source"))
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
        source: StreamType = StreamType(request.match_info.get("source"))
        body = await api_validate(SCHEMA_DEFAULT, request)

        await asyncio.shield(self.sys_host.sound.set_default(source, body[ATTR_NAME]))

    @api_process
    async def set_profile(self, request: web.Request) -> None:
        """Set audio default sources."""
        body = await api_validate(SCHEMA_PROFILE, request)

        await asyncio.shield(
            self.sys_host.sound.ativate_profile(body[ATTR_CARD], body[ATTR_NAME])
        )
