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
from ..dbus.network.interface import NetworkInterface
from ..dbus.network.utils import int2ip
from .utils import api_process, api_validate

SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional("address"): vol.Coerce(str),
        vol.Optional("mode"): vol.Coerce(str),
        vol.Optional("gateway"): vol.Coerce(str),
        vol.Optional("dns"): vol.Coerce(str),
    }
)


def interface_information(interface: NetworkInterface) -> dict:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_IP_ADDRESS: interface.ip_address,
        ATTR_GATEWAY: interface.gateway,
        ATTR_ID: interface.id,
        ATTR_TYPE: interface.type,
        "nameservers": ", ".join(int2ip(x) for x in interface.nameservers),
        "method": interface.method,
        ATTR_PRIMARY: interface.primary,
    }


class APINetwork(CoreSysAttributes):
    """Handle REST API for network."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        interfaces = {}
        for interface in self.sys_dbus.network.interfaces:
            interfaces[
                self.sys_dbus.network.interfaces[interface].name
            ] = interface_information(self.sys_dbus.network.interfaces[interface])

        return {ATTR_INTERFACES: interfaces}

    @api_process
    async def interface_info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information for a interface."""
        req_interface = request.match_info.get("interface")
        for interface in self.sys_dbus.network.interfaces:
            if req_interface == self.sys_dbus.network.interfaces[interface].name:
                return interface_information(
                    self.sys_dbus.network.interfaces[interface]
                )

        return {}

    @api_process
    async def interface_update(self, request: web.Request) -> Dict[str, Any]:
        """Update the configuration of an interface."""
        # req_interface = request.match_info.get("interface")
        req_interface = request.match_info.get("interface")

        if not self.sys_dbus.network.interfaces.get(req_interface):
            return {}

        body = await api_validate(SCHEMA_UPDATE, request)
        if not body:
            return {}

        await self.sys_dbus.network.interfaces[req_interface].update_settings(
            address=body.get("address"),
        )
        await self.sys_dbus.network.update()
        return await self.interface_info(request)
