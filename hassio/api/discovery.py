"""Init file for HassIO network rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_PROVIDER, ATTR_UUID, ATTR_COMPONENT, ATTR_PLATFORM, ATTR_CONFIG,
    REQUEST_FROM)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SCHEMA_DISCOVERY = vol.Schema({
    vol.Required(ATTR_COMPONENT): vol.Coerce(str),
    vol.Optional(ATTR_PLATFORM): vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_CONFIG): vol.Any(None, dict),
})


class APIDiscovery(CoreSysAttributes):
    """Handle rest api for discovery functions."""

    @api_process
    async def list(self, request):
        """Show register services."""
        discovery = []
        for message in self._services.discovery.list_messages:
            discovery.append({
                ATTR_PROVIDER: message.provider,
                ATTR_UUID: message.uuid,
                ATTR_COMPONENT: message.component,
                ATTR_PLATFORM: message.platform,
                ATTR_CONFIG: message.config,
            })

        return discovery

    @api_process
    async def set_discovery(self, request):
        """Write data into a discovery pipeline."""
        body = await api_validate(SCHEMA_DISCOVERY, request)

        return await asyncio.shield(
            self._servcies.discover.send(
                provider=request[REQUEST_FROM], **body),
            loop=self._loop)

    @api_process
    async def get_discovery(self, request):
        """Read data into a discovery message."""
        message  = self._services.discovery.get(request.match_info.get('uuid'))

        if not message:
            raise RuntimeError("Discovery message not found")

        return {
            ATTR_PROVIDER: message.provider,
            ATTR_UUID: message.uuid,
            ATTR_COMPONENT: message.component,
            ATTR_PLATFORM: message.platform,
            ATTR_CONFIG: message.config,
        }
