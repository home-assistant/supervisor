"""REST API for network."""

import asyncio
from collections.abc import Awaitable
from ipaddress import IPv4Address, IPv4Interface, IPv6Address, IPv6Interface
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_ACCESSPOINTS,
    ATTR_ADDR_GEN_MODE,
    ATTR_ADDRESS,
    ATTR_AUTH,
    ATTR_CONNECTED,
    ATTR_DNS,
    ATTR_DOCKER,
    ATTR_ENABLED,
    ATTR_FREQUENCY,
    ATTR_GATEWAY,
    ATTR_HOST_INTERNET,
    ATTR_ID,
    ATTR_INTERFACE,
    ATTR_INTERFACES,
    ATTR_IP6_PRIVACY,
    ATTR_IPV4,
    ATTR_IPV6,
    ATTR_MAC,
    ATTR_METHOD,
    ATTR_MODE,
    ATTR_NAMESERVERS,
    ATTR_PARENT,
    ATTR_PRIMARY,
    ATTR_PSK,
    ATTR_READY,
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
from ..exceptions import APIError, APINotFound, HostNetworkNotFound
from ..host.configuration import (
    AccessPoint,
    Interface,
    InterfaceAddrGenMode,
    InterfaceIp6Privacy,
    InterfaceMethod,
    Ip6Setting,
    IpConfig,
    IpSetting,
    VlanConfig,
    WifiConfig,
)
from ..host.const import AuthMethod, InterfaceType, WifiMode
from .utils import api_process, api_validate

_SCHEMA_IPV4_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_ADDRESS): [vol.Coerce(IPv4Interface)],
        vol.Optional(ATTR_METHOD): vol.Coerce(InterfaceMethod),
        vol.Optional(ATTR_GATEWAY): vol.Coerce(IPv4Address),
        vol.Optional(ATTR_NAMESERVERS): [vol.Coerce(IPv4Address)],
    }
)

_SCHEMA_IPV6_CONFIG = vol.Schema(
    {
        vol.Optional(ATTR_ADDRESS): [vol.Coerce(IPv6Interface)],
        vol.Optional(ATTR_METHOD): vol.Coerce(InterfaceMethod),
        vol.Optional(ATTR_ADDR_GEN_MODE): vol.Coerce(InterfaceAddrGenMode),
        vol.Optional(ATTR_IP6_PRIVACY): vol.Coerce(InterfaceIp6Privacy),
        vol.Optional(ATTR_GATEWAY): vol.Coerce(IPv6Address),
        vol.Optional(ATTR_NAMESERVERS): [vol.Coerce(IPv6Address)],
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
        vol.Optional(ATTR_IPV4): _SCHEMA_IPV4_CONFIG,
        vol.Optional(ATTR_IPV6): _SCHEMA_IPV6_CONFIG,
        vol.Optional(ATTR_WIFI): _SCHEMA_WIFI_CONFIG,
        vol.Optional(ATTR_ENABLED): vol.Boolean(),
    }
)


def ip4config_struct(config: IpConfig, setting: IpSetting) -> dict[str, Any]:
    """Return a dict with information about IPv4 configuration."""
    return {
        ATTR_METHOD: setting.method,
        ATTR_ADDRESS: [address.with_prefixlen for address in config.address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway) if config.gateway else None,
        ATTR_READY: config.ready,
    }


def ip6config_struct(config: IpConfig, setting: Ip6Setting) -> dict[str, Any]:
    """Return a dict with information about IPv6 configuration."""
    return {
        ATTR_METHOD: setting.method,
        ATTR_ADDR_GEN_MODE: setting.addr_gen_mode,
        ATTR_IP6_PRIVACY: setting.ip6_privacy,
        ATTR_ADDRESS: [address.with_prefixlen for address in config.address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway) if config.gateway else None,
        ATTR_READY: config.ready,
    }


def wifi_struct(config: WifiConfig) -> dict[str, Any]:
    """Return a dict with information about wifi configuration."""
    return {
        ATTR_MODE: config.mode,
        ATTR_AUTH: config.auth,
        ATTR_SSID: config.ssid,
        ATTR_SIGNAL: config.signal,
    }


def vlan_struct(config: VlanConfig) -> dict[str, Any]:
    """Return a dict with information about VLAN configuration."""
    return {
        ATTR_ID: config.id,
        ATTR_PARENT: config.interface,
    }


def interface_struct(interface: Interface) -> dict[str, Any]:
    """Return a dict with information of a interface to be used in th API."""
    return {
        ATTR_INTERFACE: interface.name,
        ATTR_TYPE: interface.type,
        ATTR_ENABLED: interface.enabled,
        ATTR_CONNECTED: interface.connected,
        ATTR_PRIMARY: interface.primary,
        ATTR_MAC: interface.mac,
        ATTR_IPV4: ip4config_struct(interface.ipv4, interface.ipv4setting)
        if interface.ipv4 and interface.ipv4setting
        else None,
        ATTR_IPV6: ip6config_struct(interface.ipv6, interface.ipv6setting)
        if interface.ipv6 and interface.ipv6setting
        else None,
        ATTR_WIFI: wifi_struct(interface.wifi) if interface.wifi else None,
        ATTR_VLAN: vlan_struct(interface.vlan) if interface.vlan else None,
    }


def accesspoint_struct(accesspoint: AccessPoint) -> dict[str, Any]:
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
        if name.lower() == "default":
            for interface in self.sys_host.network.interfaces:
                if not interface.primary:
                    continue
                return interface

        else:
            try:
                return self.sys_host.network.get(name)
            except HostNetworkNotFound:
                pass

        raise APINotFound(f"Interface {name} does not exist") from None

    @api_process
    async def info(self, request: web.Request) -> dict[str, Any]:
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
    async def interface_info(self, request: web.Request) -> dict[str, Any]:
        """Return network information for a interface."""
        interface = self._get_interface(request.match_info[ATTR_INTERFACE])

        return interface_struct(interface)

    @api_process
    async def interface_update(self, request: web.Request) -> None:
        """Update the configuration of an interface."""
        interface = self._get_interface(request.match_info[ATTR_INTERFACE])

        # Validate data
        body = await api_validate(SCHEMA_UPDATE, request)
        if not body:
            raise APIError("You need to supply at least one option to update")

        # Apply config
        for key, config in body.items():
            if key == ATTR_IPV4:
                interface.ipv4setting = IpSetting(
                    method=config.get(ATTR_METHOD, InterfaceMethod.STATIC),
                    address=config.get(ATTR_ADDRESS, []),
                    gateway=config.get(ATTR_GATEWAY),
                    nameservers=config.get(ATTR_NAMESERVERS, []),
                )
            elif key == ATTR_IPV6:
                interface.ipv6setting = Ip6Setting(
                    method=config.get(ATTR_METHOD, InterfaceMethod.STATIC),
                    addr_gen_mode=config.get(
                        ATTR_ADDR_GEN_MODE, InterfaceAddrGenMode.DEFAULT
                    ),
                    ip6_privacy=config.get(
                        ATTR_IP6_PRIVACY, InterfaceIp6Privacy.DEFAULT
                    ),
                    address=config.get(ATTR_ADDRESS, []),
                    gateway=config.get(ATTR_GATEWAY),
                    nameservers=config.get(ATTR_NAMESERVERS, []),
                )
            elif key == ATTR_WIFI:
                interface.wifi = WifiConfig(
                    mode=config.get(ATTR_MODE, WifiMode.INFRASTRUCTURE),
                    ssid=config.get(ATTR_SSID, ""),
                    auth=config.get(ATTR_AUTH, AuthMethod.OPEN),
                    psk=config.get(ATTR_PSK, None),
                    signal=None,
                )
            elif key == ATTR_ENABLED:
                interface.enabled = config

        await asyncio.shield(self.sys_host.network.apply_changes(interface))

    @api_process
    def reload(self, request: web.Request) -> Awaitable[None]:
        """Reload network data."""
        return asyncio.shield(
            self.sys_host.network.update(force_connectivity_check=True)
        )

    @api_process
    async def scan_accesspoints(self, request: web.Request) -> dict[str, Any]:
        """Scan and return a list of available networks."""
        interface = self._get_interface(request.match_info[ATTR_INTERFACE])

        # Only wlan is supported
        if interface.type != InterfaceType.WIRELESS:
            raise APIError(f"Interface {interface.name} is not a valid wireless card!")

        ap_list = await self.sys_host.network.scan_wifi(interface)

        return {ATTR_ACCESSPOINTS: [accesspoint_struct(ap) for ap in ap_list]}

    @api_process
    async def create_vlan(self, request: web.Request) -> None:
        """Create a new vlan."""
        interface = self._get_interface(request.match_info[ATTR_INTERFACE])
        vlan = int(request.match_info.get(ATTR_VLAN, -1))
        if vlan < 0:
            raise APIError(f"Invalid vlan specified: {vlan}")

        # Only ethernet is supported
        if interface.type != InterfaceType.ETHERNET:
            raise APIError(
                f"Interface {interface.name} is not a valid ethernet card for vlan!"
            )
        body = await api_validate(SCHEMA_UPDATE, request)

        vlan_config = VlanConfig(vlan, interface.name)

        ipv4_setting = None
        if ATTR_IPV4 in body:
            ipv4_setting = IpSetting(
                method=body[ATTR_IPV4].get(ATTR_METHOD, InterfaceMethod.AUTO),
                address=body[ATTR_IPV4].get(ATTR_ADDRESS, []),
                gateway=body[ATTR_IPV4].get(ATTR_GATEWAY, None),
                nameservers=body[ATTR_IPV4].get(ATTR_NAMESERVERS, []),
            )

        ipv6_setting = None
        if ATTR_IPV6 in body:
            ipv6_setting = Ip6Setting(
                method=body[ATTR_IPV6].get(ATTR_METHOD, InterfaceMethod.AUTO),
                addr_gen_mode=body[ATTR_IPV6].get(
                    ATTR_ADDR_GEN_MODE, InterfaceAddrGenMode.DEFAULT
                ),
                ip6_privacy=body[ATTR_IPV6].get(
                    ATTR_IP6_PRIVACY, InterfaceIp6Privacy.DEFAULT
                ),
                address=body[ATTR_IPV6].get(ATTR_ADDRESS, []),
                gateway=body[ATTR_IPV6].get(ATTR_GATEWAY, None),
                nameservers=body[ATTR_IPV6].get(ATTR_NAMESERVERS, []),
            )

        vlan_interface = Interface(
            "",
            "",
            "",
            True,
            True,
            False,
            InterfaceType.VLAN,
            None,
            ipv4_setting,
            None,
            ipv6_setting,
            None,
            vlan_config,
        )
        await asyncio.shield(self.sys_host.network.apply_changes(vlan_interface))
