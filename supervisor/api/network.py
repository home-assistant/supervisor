"""REST API for network."""
from typing import Any, Dict

from aiohttp import web

from ..const import (
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_INTERFACES,
    ATTR_IP_ADDRESS,
    ATTR_PRIMARY,
    ATTR_TYPE,
)
from ..coresys import CoreSysAttributes
from .utils import api_process


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
    async def interface_set(self, request: web.Request) -> Dict[str, Any]:
        """Set the IP of an interface."""
        # req_interface = request.match_info.get("interface")
        await self.sys_dbus.network.interfaces[0].update_settings(
            "192.168.2.149", "", []
        )
        await self.sys_dbus.network.update()
