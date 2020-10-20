"""REST API for network."""
import asyncio
from typing import Any, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ADDRESS,
    ATTR_DNS,
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_INTERFACE,
    ATTR_INTERFACES,
    ATTR_IP_ADDRESS,
    ATTR_METHOD,
    ATTR_METHODS,
    ATTR_NAMESERVERS,
    ATTR_PRIMARY,
    ATTR_SYSTEM,
    ATTR_TYPE,
    DOCKER_NETWORK,
    DOCKER_NETWORK_MASK,
)
from ..coresys import CoreSysAttributes
from ..dbus.const import InterfaceMethodSimple
from ..dbus.network.interface import NetworkInterface
from ..dbus.network.utils import int2ip
from ..exceptions import APIError
from .utils import api_process, api_validate

SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional(ATTR_ADDRESS): vol.Coerce(str),
        vol.Optional(ATTR_METHOD): vol.In(ATTR_METHODS),
        vol.Optional(ATTR_GATEWAY): vol.Coerce(str),
        vol.Optional(ATTR_DNS): [str],
    }
)


def interface_information(interface: NetworkInterface) -> dict:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_INTERFACE: interface.name,
        ATTR_IP_ADDRESS: f"{interface.ip_address}/{interface.prefix}",
        ATTR_GATEWAY: interface.gateway,
        ATTR_ID: interface.id,
        ATTR_TYPE: interface.type,
        ATTR_NAMESERVERS: [int2ip(x) for x in interface.nameservers],
        ATTR_METHOD: InterfaceMethodSimple.DHCP
        if interface.method == "auto"
        else InterfaceMethodSimple.STATIC,
        ATTR_PRIMARY: interface.primary,
    }


class APINetwork(CoreSysAttributes):
    """Handle REST API for network."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        interfaces = {}
        for interface in self.sys_host.network.interfaces:
            interfaces[
                self.sys_host.network.interfaces[interface].name
            ] = interface_information(self.sys_host.network.interfaces[interface])

        return {
            ATTR_INTERFACES: interfaces,
            ATTR_SYSTEM: {
                ATTR_INTERFACE: DOCKER_NETWORK,
                ATTR_ADDRESS: DOCKER_NETWORK_MASK,
                ATTR_GATEWAY: self.sys_docker.network.gateway,
                ATTR_DNS: self.sys_docker.network.dns,
            },
        }

    @api_process
    async def interface_info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information for a interface."""
        req_interface = request.match_info.get(ATTR_INTERFACE)

        if req_interface.lower() == "default":
            for interface in self.sys_host.network.interfaces:
                if not self.sys_host.network.interfaces[interface].primary:
                    continue
                return interface_information(
                    self.sys_host.network.interfaces[interface]
                )

        else:
            for interface in self.sys_host.network.interfaces:
                if req_interface != self.sys_host.network.interfaces[interface].name:
                    continue
                return interface_information(
                    self.sys_host.network.interfaces[interface]
                )

        return {}

    @api_process
    async def interface_update(self, request: web.Request) -> Dict[str, Any]:
        """Update the configuration of an interface."""
        req_interface = request.match_info.get(ATTR_INTERFACE)

        if not self.sys_host.network.interfaces.get(req_interface):
            raise APIError(f"Interface {req_interface} does not exsist")

        args = await api_validate(SCHEMA_UPDATE, request)
        if not args:
            raise APIError("You need to supply at least one option to update")

        await asyncio.shield(
            self.sys_host.network.interfaces[req_interface].update_settings(**args)
        )

        await asyncio.shield(self.sys_host.reload())

        return await asyncio.shield(self.interface_info(request))
