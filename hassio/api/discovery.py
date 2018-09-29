"""Init file for Hass.io network RESTful API."""
import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_PROVIDER, ATTR_UUID, ATTR_COMPONENT, ATTR_PLATFORM, ATTR_CONFIG,
    ATTR_DISCOVERY, ATTR_SERVICE, REQUEST_FROM)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, APIForbidden
from ..services.validate import SERVICE_ALL


SCHEMA_DISCOVERY = vol.Schema({
    vol.Required(ATTR_SERVICE): vol.In(SERVICE_ALL),
    vol.Required(ATTR_COMPONENT): vol.Coerce(str),
    vol.Optional(ATTR_PLATFORM): vol.Maybe(vol.Coerce(str)),
    vol.Optional(ATTR_CONFIG): vol.Maybe(dict),
})


class APIDiscovery(CoreSysAttributes):
    """Handle RESTful API for discovery functions."""

    def _extract_message(self, request):
        """Extract discovery message from URL."""
        message = self.sys_discovery.get(request.match_info.get('uuid'))
        if not message:
            raise APIError("Discovery message not found")
        return message

    def _check_permission_ha(self, request):
        """Check permission for API call / Home Assistant."""
        provider = request[REQUEST_FROM]
        if provider != self.sys_homeassistant:
            raise APIForbidden("Only HomeAssistant can use this API!")

    @api_process
    async def list(self, request):
        """Show register services."""
        self._check_permission_ha(request)

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
        provider = request[REQUEST_FROM]

        # Access?
        if body[ATTR_SERVICE] not in provider.discovery:
            raise APIForbidden(f"Can't use discovery!")

        # Process discovery message
        message = self.sys_discovery.send(provider=provider, **body)

        return {ATTR_UUID: message.uuid}

    @api_process
    async def get_discovery(self, request):
        """Read data into a discovery message."""
        message = self._extract_message(request)

        # HomeAssistant?
        self._check_permission_ha(request)

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
        provider = request[REQUEST_FROM]

        # Permission
        if message.provider != provider.slug:
            raise APIForbidden(f"Can't remove discovery message")

        self.sys_discovery.remove(message)
        return True
