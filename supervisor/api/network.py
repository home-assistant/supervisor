"""REST API for network."""
from typing import Any, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_INTERFACES,
    ATTR_IP_ADDRESS,
    ATTR_PRIMARY,
    ATTR_TYPE,
)
from ..coresys import CoreSysAttributes
from .utils import api_process, api_validate

SCHEMA_SET = vol.Schema(
    {
        vol.Optional("address"): vol.Coerce(str),
        vol.Optional("mode"): vol.Coerce(str),
        vol.Optional("gateway"): vol.Coerce(str),
        vol.Optional("dns"): vol.Coerce(str),
    }
)


class APINetwork(CoreSysAttributes):
    """Handle REST API for network."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        interfaces = {}
        for interface in self.sys_dbus.network.interfaces:
            interfaces[interface.name] = {
                ATTR_IP_ADDRESS: interface.ip_address,
                ATTR_GATEWAY: interface.gateway,
                ATTR_ID: interface.id,
                ATTR_TYPE: interface.type,
                ATTR_PRIMARY: interface.primary,
            }

        return {ATTR_INTERFACES: interfaces}

    @api_process
    async def interface_info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information for a interface."""
        req_interface = request.match_info.get("interface")
        for interface in self.sys_dbus.network.interfaces:
            if req_interface == interface.name:
                return {
                    ATTR_IP_ADDRESS: interface.ip_address,
                    ATTR_GATEWAY: interface.gateway,
                    ATTR_ID: interface.id,
                    ATTR_TYPE: interface.type,
                    ATTR_PRIMARY: interface.primary,
                }

        return {}

    @api_process
    async def interface_update(self, request: web.Request) -> Dict[str, Any]:
        """Update the configuration of an interface."""
        # req_interface = request.match_info.get("interface")
        req_interface = request.match_info.get("interface")

        if req_interface not in [x.name for x in self.sys_dbus.network.interfaces]:
            return {}

        body = await api_validate(SCHEMA_SET, request)
        if not body:
            return {}

        await self.sys_dbus.network.interfaces[0].update_settings(
            address=body.get("address"),
        )
        await self.sys_dbus.network.update()
        return await self.interface_info(request)
