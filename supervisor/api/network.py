"""REST API for network."""
import asyncio
from typing import Any, Dict

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ADDRESS,
    ATTR_DNS,
    ATTR_DOCKER,
    ATTR_GATEWAY,
    ATTR_ID,
    ATTR_INTERFACE,
    ATTR_INTERFACES,
    ATTR_IP_ADDRESS,
    ATTR_IPV4,
    ATTR_IPV6,
    ATTR_METHOD,
    ATTR_METHODS,
    ATTR_MODE,
    ATTR_NAMESERVERS,
    ATTR_PRIMARY,
    ATTR_TYPE,
    DOCKER_NETWORK,
    DOCKER_NETWORK_MASK,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError
from ..host.network import Interface, IpConfig
from .utils import api_process, api_validate

SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional(ATTR_ADDRESS): vol.Coerce(str),
        vol.Optional(ATTR_METHOD): vol.In(ATTR_METHODS),
        vol.Optional(ATTR_GATEWAY): vol.Coerce(str),
        vol.Optional(ATTR_DNS): [str],
    }
)


def ipconfig_struct(config: IpConfig) -> dict:
    """Return a dict with information about ip configuration."""
    return {
        ATTR_MODE: config.mode,
        ATTR_IP_ADDRESS: [address.with_prefixlen for address in config.address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway),
    }


def interface_struct(interface: Interface) -> dict:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_ID: interface.id,
        ATTR_INTERFACE: interface.name,
        ATTR_TYPE: interface.type,
        ATTR_PRIMARY: interface.primary,
        ATTR_IPV4: ipconfig_struct(interface.ipv4),
        ATTR_IPV6: ipconfig_struct(interface.ipv6),
    }


class APINetwork(CoreSysAttributes):
    """Handle REST API for network."""

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        interfaces = {}
        for interface in self.sys_host.network.interfaces:
            interfaces[interface.name] = interface_struct(interface)

        return {
            ATTR_INTERFACES: interfaces,
            ATTR_DOCKER: {
                ATTR_INTERFACE: DOCKER_NETWORK,
                ATTR_ADDRESS: str(DOCKER_NETWORK_MASK),
                ATTR_GATEWAY: str(self.sys_docker.network.gateway),
                ATTR_DNS: str(self.sys_docker.network.dns),
            },
        }

    @api_process
    async def interface_info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information for a interface."""
        req_interface = request.match_info.get(ATTR_INTERFACE)

        if req_interface.lower() == "default":
            for interface in self.sys_host.network.interfaces:
                if not interface.primary:
                    continue
                return interface_struct(interface)

        else:
            for interface in self.sys_host.network.interfaces:
                if req_interface != interface.name:
                    continue
                return interface_struct(interface)

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
