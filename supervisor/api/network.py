"""REST API for network."""
from typing import Any, Dict

from aiohttp import web

from ..const import ATTR_IP_ADDRESS
from ..coresys import CoreSysAttributes
from ..dbus.network.const import (
    ATTR_CONNECTIONS,
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_PRIMARY_CONNECTION,
    ATTR_TYPE,
)
from .utils import api_process


class APINetwork(CoreSysAttributes):
    """Handle REST API for network."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        primary = self.sys_dbus.network.primary_connection
        connections = []
        for connection in self.sys_dbus.network.connections:
            connections.append(
                {
                    ATTR_IP_ADDRESS: connection.ip4_config.address_data[0].address,
                    ATTR_GATEWAY: connection.ip4_config.gateway,
                    ATTR_ID: connection.id,
                    ATTR_TYPE: connection.type,
                }
            )

        return {
            ATTR_PRIMARY_CONNECTION: {
                ATTR_IP_ADDRESS: primary.ip4_config.address_data[0].address,
                ATTR_GATEWAY: primary.ip4_config.gateway,
                ATTR_ID: primary.id,
                ATTR_TYPE: primary.type,
            },
            ATTR_CONNECTIONS: connections,
        }
