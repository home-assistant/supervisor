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
