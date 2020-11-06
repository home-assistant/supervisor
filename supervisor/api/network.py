"""REST API for network."""
import asyncio
from ipaddress import ip_address, ip_interface
from typing import Any, Dict

from aiohttp import web
import attr
import voluptuous as vol

from ..const import (
    ATTR_ADDRESS,
    ATTR_AUTH,
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
    ATTR_MODE,
    ATTR_NAMESERVERS,
    ATTR_PRIMARY,
    ATTR_PRIVACY,
    ATTR_PSK,
    ATTR_SSID,
    ATTR_TYPE,
    ATTR_WIFI,
    DOCKER_NETWORK,
    DOCKER_NETWORK_MASK,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, HostNetworkNotFound
from ..host.const import AuthMethod, WifiMode
from ..host.network import Interface, InterfaceMethod, IpConfig, WifiConfig
from .utils import api_process, api_validate

_SCHEMA_IP_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_ADDRESS): [vol.Coerce(ip_interface)],
        vol.Optional(ATTR_METHOD): vol.Coerce(InterfaceMethod),
        vol.Optional(ATTR_GATEWAY): vol.Coerce(ip_address),
        vol.Optional(ATTR_NAMESERVERS): [vol.Coerce(ip_address)],
    }
)

_SCHEMA_WIFI_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_MODE): vol.Coerce(WifiMode),
        vol.Optional(ATTR_AUTH): vol.Coerce(AuthMethod),
        vol.Optional(ATTR_SSID): str,
        vol.Optional(ATTR_PSK): str,
    }
)

# pylint: disable=no-value-for-parameter
SCHEMA_UPDATE = vol.Schema(
    {
        vol.Optional(ATTR_IPV4): _SCHEMA_IP_CONFIG,
        vol.Optional(ATTR_IPV6): _SCHEMA_IP_CONFIG,
        vol.Optional(ATTR_WIFI): _SCHEMA_WIFI_CONFIG,
        vol.Optional(ATTR_PRIVACY): vol.Boolean(),
    }
)


def ipconfig_struct(config: IpConfig) -> dict:
    """Return a dict with information about ip configuration."""
    return {
        ATTR_METHOD: config.mode,
        ATTR_IP_ADDRESS: [address.with_prefixlen for address in config.ip_address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway),
    }


def wifi_struct(config: WifiConfig) -> dict:
    """Return a dict with information about wifi configuration."""
    return {ATTR_MODE: config.mode, ATTR_AUTH: config.auth, ATTR_SSID: config.ssid}


def interface_struct(interface: Interface) -> dict:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_ID: interface.id,
        ATTR_INTERFACE: interface.name,
        ATTR_TYPE: interface.type,
        ATTR_PRIMARY: interface.primary,
        ATTR_PRIVACY: interface.privacy,
        ATTR_IPV4: ipconfig_struct(interface.ipv4),
        ATTR_IPV6: ipconfig_struct(interface.ipv6),
        ATTR_WIFI: wifi_struct(interface.wifi) if interface.wifi else None,
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

        # Validate interface
        try:
            interface = self.sys_host.network.get(req_interface)
        except HostNetworkNotFound:
            raise APIError(f"Interface {req_interface} does not exsist") from None

        # Validate data
        body = await api_validate(SCHEMA_UPDATE, request)
        if not body:
            raise APIError("You need to supply at least one option to update")

        # Apply config
        for key, config in body.items():
            if key == ATTR_IPV4:
                interface.ipv4 = attr.evolve(interface.ipv4, **config)
            elif key == ATTR_IPV6:
                interface.ipv6 = attr.evolve(interface.ipv6, **config)
            elif key == ATTR_WIFI:
                interface.wifi = attr.evolve(interface.wifi, **config)
            elif key == ATTR_PRIVACY:
                interface.privacy = config

        await asyncio.shield(self.sys_host.network.apply_change(interface))
