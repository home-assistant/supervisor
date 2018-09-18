"""Init file for Hass.io network RESTful API."""
import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_PROVIDER, ATTR_UUID, ATTR_COMPONENT, ATTR_PLATFORM, ATTR_CONFIG,
    ATTR_DISCOVERY, REQUEST_FROM)
from ..coresys import CoreSysAttributes


SCHEMA_DISCOVERY = vol.Schema({
    vol.Required(ATTR_COMPONENT): vol.Coerce(str),
    vol.Optional(ATTR_PLATFORM): vol.Any(None, vol.Coerce(str)),
    vol.Optional(ATTR_CONFIG): vol.Any(None, dict),
})


class APIDiscovery(CoreSysAttributes):
    """Handle RESTful API for discovery functions."""

    def _extract_message(self, request):
        """Extract discovery message from URL."""
        message = self.sys_discovery.get(request.match_info.get('uuid'))
        if not message:
            raise RuntimeError("Discovery message not found")
        return message

    @api_process
    async def list(self, request):
        """Show register services."""
        discovery = []
        for message in self.sys_discovery.list_messages:
            discovery.append({
                ATTR_PROVIDER: message.provider,
                ATTR_UUID: message.uuid,
                ATTR_COMPONENT: message.component,
                ATTR_PLATFORM: message.platform,
                ATTR_CONFIG: message.config,
            })

        return {ATTR_DISCOVERY: discovery}

    @api_process
    async def set_discovery(self, request):
        """Write data into a discovery pipeline."""
        body = await api_validate(SCHEMA_DISCOVERY, request)
        message = self.sys_discovery.send(
            provider=request[REQUEST_FROM], **body)

        return {ATTR_UUID: message.uuid}

    @api_process
    async def get_discovery(self, request):
        """Read data into a discovery message."""
        message = self._extract_message(request)

        return {
            ATTR_PROVIDER: message.provider,
            ATTR_UUID: message.uuid,
            ATTR_COMPONENT: message.component,
            ATTR_PLATFORM: message.platform,
            ATTR_CONFIG: message.config,
        }

    @api_process
    async def del_discovery(self, request):
        """Delete data into a discovery message."""
        message = self._extract_message(request)

        self.sys_discovery.remove(message)
        return True
