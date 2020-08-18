"""REST API for network."""
from typing import Any, Dict

from aiohttp import web

from ..const import (
    ATTR_CONNECTIONS,
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_INTERFACE,
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
        connections = []
        for connection in self.sys_dbus.network.connections:
            connections.append(
                {
                    ATTR_IP_ADDRESS: connection.ip4_config.address_data[0].address,
                    ATTR_GATEWAY: connection.ip4_config.gateway,
                    ATTR_ID: connection.id,
                    ATTR_INTERFACE: connection.device.interface,
                    ATTR_TYPE: connection.type,
                    ATTR_PRIMARY: connection.primary,
                }
            )

        return {ATTR_CONNECTIONS: connections}
