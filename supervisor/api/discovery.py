"""Init file for Supervisor network RESTful API."""

import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..apps.app import App
from ..const import (
    ATTR_ADDON,
    ATTR_APP,
    ATTR_CONFIG,
    ATTR_DISCOVERY,
    ATTR_SERVICE,
    ATTR_SERVICES,
    ATTR_UUID,
    REQUEST_FROM,
    AppState,
)
from ..coresys import CoreSysAttributes
from ..discovery import Message
from ..exceptions import APIForbidden, APINotFound
from .utils import api_process, api_validate, require_home_assistant

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_DISCOVERY = vol.Schema(
    {
        vol.Required(ATTR_SERVICE): str,
        vol.Required(ATTR_CONFIG): dict,
    }
)


class APIDiscovery(CoreSysAttributes):
    """Handle RESTful API for discovery functions."""

    def _extract_message(self, request: web.Request) -> Message:
        """Extract discovery message from URL."""
        message = self.sys_discovery.get(request.match_info["uuid"])
        if not message:
            raise APINotFound("Discovery message not found")
        return message

    def _message_data(self, message: Message) -> dict[str, Any]:
        """Return discovery message data in V2 format."""
        return {
            ATTR_APP: message.app,
            ATTR_SERVICE: message.service,
            ATTR_UUID: message.uuid,
            ATTR_CONFIG: message.config,
        }

    def _available_services(self) -> dict[str, list[str]]:
        """Return available discovery services keyed by service name."""
        services: dict[str, list[str]] = {}
        for app in self.sys_apps.all:
            for name in app.discovery:
                services.setdefault(name, []).append(app.slug)
        return services

    def _list_messages(self) -> list[dict[str, Any]]:
        """Return discovery messages for started apps in V2 format."""
        return [
            self._message_data(message)
            for message in self.sys_discovery.list_messages
            if (discovered := self.sys_apps.get_local_only(message.app))
            and discovered.state == AppState.STARTED
        ]

    @api_process
    @require_home_assistant
    async def list_discovery(self, request: web.Request) -> dict[str, Any]:
        """Show registered discovery (v2: uses "app" key)."""
        return {
            ATTR_DISCOVERY: self._list_messages(),
            ATTR_SERVICES: self._available_services(),
        }

    @api_process
    @require_home_assistant
    async def list_discovery_v1(self, request: web.Request) -> dict[str, Any]:
        """Show registered discovery (v1: uses "addon" key)."""
        messages = [
            {ATTR_ADDON: m[ATTR_APP], **{k: v for k, v in m.items() if k != ATTR_APP}}
            for m in self._list_messages()
        ]
        return {ATTR_DISCOVERY: messages, ATTR_SERVICES: self._available_services()}

    @api_process
    async def set_discovery(self, request: web.Request) -> dict[str, str]:
        """Write data into a discovery pipeline."""
        body = await api_validate(SCHEMA_DISCOVERY, request)
        app: App = request[REQUEST_FROM]
        service = body[ATTR_SERVICE]

        # Access?
        if body[ATTR_SERVICE] not in app.discovery:
            _LOGGER.error(
                "App %s attempted to send discovery for service %s which is not listed in its config. Please report this to the maintainer of the app",
                app.name,
                service,
            )
            raise APIForbidden(
                "Apps must list services they provide via discovery in their config!"
            )

        # Process discovery message
        message = await self.sys_discovery.send(app, **body)

        return {ATTR_UUID: message.uuid}

    @api_process
    @require_home_assistant
    async def get_discovery(self, request: web.Request) -> dict[str, Any]:
        """Read a discovery message (v2: uses "app" key)."""
        return self._message_data(self._extract_message(request))

    @api_process
    @require_home_assistant
    async def get_discovery_v1(self, request: web.Request) -> dict[str, Any]:
        """Read a discovery message (v1: uses "addon" key)."""
        data = self._message_data(self._extract_message(request))
        data[ATTR_ADDON] = data.pop(ATTR_APP)
        return data

    @api_process
    async def del_discovery(self, request: web.Request) -> None:
        """Delete data into a discovery message."""
        message = self._extract_message(request)
        app = request[REQUEST_FROM]

        # Permission
        if message.app != app.slug:
            raise APIForbidden("Can't remove discovery message")

        await self.sys_discovery.remove(message)
