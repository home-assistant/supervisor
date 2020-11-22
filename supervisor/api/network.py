"""REST API for network."""
import asyncio
from ipaddress import ip_address, ip_interface
from typing import Any, Dict

from aiohttp import web
import attr
import voluptuous as vol

from ..const import (
    ATTR_ACCESSPOINTS,
    ATTR_ADDRESS,
    ATTR_AUTH,
    ATTR_CONNECTED,
    ATTR_DNS,
    ATTR_DOCKER,
    ATTR_ENABLED,
    ATTR_FREQUENCY,
    ATTR_GATEWAY,
    ATTR_HOST_INTERNET,
    ATTR_INTERFACE,
    ATTR_INTERFACES,
    ATTR_IPV4,
    ATTR_IPV6,
    ATTR_MAC,
    ATTR_METHOD,
    ATTR_MODE,
    ATTR_NAMESERVERS,
    ATTR_PRIMARY,
    ATTR_PSK,
    ATTR_SIGNAL,
    ATTR_SSID,
    ATTR_SUPERVISOR_INTERNET,
    ATTR_TYPE,
    ATTR_VLAN,
    ATTR_WIFI,
    DOCKER_NETWORK,
    DOCKER_NETWORK_MASK,
)
from ..coresys import CoreSysAttributes
from ..exceptions import APIError, HostNetworkNotFound
from ..host.const import AuthMethod, InterfaceType, WifiMode
from ..host.network import (
    AccessPoint,
    Interface,
    InterfaceMethod,
    IpConfig,
    VlanConfig,
    WifiConfig,
)
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
        vol.Optional(ATTR_ENABLED): vol.Boolean(),
    }
)


def ipconfig_struct(config: IpConfig) -> dict:
    """Return a dict with information about ip configuration."""
    return {
        ATTR_METHOD: config.method,
        ATTR_ADDRESS: [address.with_prefixlen for address in config.address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway) if config.gateway else None,
    }


def wifi_struct(config: WifiConfig) -> dict:
    """Return a dict with information about wifi configuration."""
    return {
        ATTR_MODE: config.mode,
        ATTR_AUTH: config.auth,
        ATTR_SSID: config.ssid,
        ATTR_SIGNAL: config.signal,
    }


def interface_struct(interface: Interface) -> dict:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_INTERFACE: interface.name,
        ATTR_TYPE: interface.type,
        ATTR_ENABLED: interface.enabled,
        ATTR_CONNECTED: interface.connected,
        ATTR_PRIMARY: interface.primary,
        ATTR_IPV4: ipconfig_struct(interface.ipv4) if interface.ipv4 else None,
        ATTR_IPV6: ipconfig_struct(interface.ipv6) if interface.ipv6 else None,
        ATTR_WIFI: wifi_struct(interface.wifi) if interface.wifi else None,
        ATTR_VLAN: wifi_struct(interface.vlan) if interface.vlan else None,
    }


def accesspoint_struct(accesspoint: AccessPoint) -> dict:
    """Return a dict for AccessPoint."""
    return {
        ATTR_MODE: accesspoint.mode,
        ATTR_SSID: accesspoint.ssid,
        ATTR_FREQUENCY: accesspoint.frequency,
        ATTR_SIGNAL: accesspoint.signal,
        ATTR_MAC: accesspoint.mac,
    }


class APINetwork(CoreSysAttributes):
    """Handle REST API for network."""

    def _get_interface(self, name: str) -> Interface:
        """Get Interface by name or default."""
        name = name.lower()

        if name == "default":
            for interface in self.sys_host.network.interfaces:
                if not interface.primary:
                    continue
                return interface

        else:
            try:
                return self.sys_host.network.get(name)
            except HostNetworkNotFound:
                pass

        raise APIError(f"Interface {name} does not exsist") from None

    @api_process
    async def info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information."""
        return {
            ATTR_INTERFACES: [
                interface_struct(interface)
                for interface in self.sys_host.network.interfaces
            ],
            ATTR_DOCKER: {
                ATTR_INTERFACE: DOCKER_NETWORK,
                ATTR_ADDRESS: str(DOCKER_NETWORK_MASK),
                ATTR_GATEWAY: str(self.sys_docker.network.gateway),
                ATTR_DNS: str(self.sys_docker.network.dns),
            },
            ATTR_HOST_INTERNET: self.sys_host.network.connectivity,
            ATTR_SUPERVISOR_INTERNET: self.sys_supervisor.connectivity,
        }

    @api_process
    async def interface_info(self, request: web.Request) -> Dict[str, Any]:
        """Return network information for a interface."""
        interface = self._get_interface(request.match_info.get(ATTR_INTERFACE))

        return interface_struct(interface)

    @api_process
    async def interface_update(self, request: web.Request) -> None:
        """Update the configuration of an interface."""
        interface = self._get_interface(request.match_info.get(ATTR_INTERFACE))

        # Validate data
        body = await api_validate(SCHEMA_UPDATE, request)
        if not body:
            raise APIError("You need to supply at least one option to update")

        # Apply config
        for key, config in body.items():
            if key == ATTR_IPV4:
                interface.ipv4 = attr.evolve(
                    interface.ipv4 or IpConfig(InterfaceMethod.STATIC, [], None, []),
                    **config,
                )
            elif key == ATTR_IPV6:
                interface.ipv6 = attr.evolve(
                    interface.ipv6 or IpConfig(InterfaceMethod.STATIC, [], None, []),
                    **config,
                )
            elif key == ATTR_WIFI:
                interface.wifi = attr.evolve(
                    interface.wifi
                    or WifiConfig(
                        WifiMode.INFRASTRUCTURE, "", AuthMethod.OPEN, None, None
                    ),
                    **config,
                )
            elif key == ATTR_ENABLED:
                interface.enabled = config

            if not interface.enabled and (
                interface.ipv4.method
                in [
                    InterfaceMethod.STATIC,
                    InterfaceMethod.AUTO,
                ]
                or interface.ipv6.method
                in [
                    InterfaceMethod.STATIC,
                    InterfaceMethod.AUTO,
                ]
            ):
                interface.enabled = True

        await asyncio.shield(self.sys_host.network.apply_changes(interface))

    @api_process
    async def scan_accesspoints(self, request: web.Request) -> Dict[str, Any]:
        """Scan and return a list of available networks."""
        interface = self._get_interface(request.match_info.get(ATTR_INTERFACE))

        # Only wlan is supported
        if interface.type != InterfaceType.WIRELESS:
            raise APIError(f"Interface {interface.name} is not a valid wireless card!")

        ap_list = await self.sys_host.network.scan_wifi(interface)

        return {ATTR_ACCESSPOINTS: [accesspoint_struct(ap) for ap in ap_list]}

    @api_process
    async def create_vlan(self, request: web.Request) -> None:
        """Create a new vlan."""
        interface = self._get_interface(request.match_info.get(ATTR_INTERFACE))
        vlan = int(request.match_info.get(ATTR_VLAN))

        # Only ethernet is supported
        if interface.type != InterfaceType.ETHERNET:
            raise APIError(
                f"Interface {interface.name} is not a valid ethernet card for vlan!"
            )
        body = await api_validate(SCHEMA_UPDATE, request)

        vlan_config = VlanConfig(vlan, interface.name)

        ipv4_config = None
        if ATTR_IPV4 in body:
            ipv4_config = IpConfig(
                body[ATTR_IPV4].get(ATTR_METHOD, InterfaceMethod.AUTO),
                body[ATTR_IPV4].get(ATTR_ADDRESS, []),
                body[ATTR_IPV4].get(ATTR_GATEWAY, None),
                body[ATTR_IPV4].get(ATTR_NAMESERVERS, []),
            )

        ipv6_config = None
        if ATTR_IPV6 in body:
            ipv6_config = IpConfig(
                body[ATTR_IPV6].get(ATTR_METHOD, InterfaceMethod.AUTO),
                body[ATTR_IPV6].get(ATTR_ADDRESS, []),
                body[ATTR_IPV6].get(ATTR_GATEWAY, None),
                body[ATTR_IPV6].get(ATTR_NAMESERVERS, []),
            )

        vlan_interface = Interface(
            "",
            True,
            True,
            False,
            InterfaceType.VLAN,
            ipv4_config,
            ipv6_config,
            None,
            vlan_config,
        )
        await asyncio.shield(self.sys_host.network.apply_changes(vlan_interface))
