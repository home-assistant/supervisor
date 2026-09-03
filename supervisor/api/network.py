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
    ATTR_ADDRESSES,
    ATTR_AUTH,
    ATTR_CONFIG,
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
    ATTR_LLMNR,
    ATTR_MAC,
    ATTR_MDNS,
    ATTR_METHOD,
    ATTR_MODE,
    ATTR_NAME,
    ATTR_NAMESERVERS,
    ATTR_PARENT,
    ATTR_PATH,
    ATTR_PRIMARY,
    ATTR_PSK,
    ATTR_PSK_SET,
    ATTR_READY,
    ATTR_ROUTE_METRIC,
    ATTR_SIGNAL,
    ATTR_SSID,
    ATTR_STATE,
    ATTR_SUPERVISOR_INTERNET,
    ATTR_TYPE,
    ATTR_VLAN,
    ATTR_WIFI,
    DOCKER_IPV4_NETWORK_MASK,
    DOCKER_NETWORK,
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
    MulticastDnsMode,
    ResolvedInterface,
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
        vol.Optional(ATTR_ROUTE_METRIC): vol.Coerce(int),
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
        vol.Optional(ATTR_ROUTE_METRIC): vol.Coerce(int),
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
        vol.Optional(ATTR_MDNS): vol.Coerce(MulticastDnsMode),
        vol.Optional(ATTR_LLMNR): vol.Coerce(MulticastDnsMode),
    }
)


def _validate_ip_config_v2(schema_key: str):
    """Return a validator rejecting cross-field contradictions in a v2 IP config block."""

    def validator(config: dict[str, Any]) -> dict[str, Any]:
        addresses = config.get(ATTR_ADDRESSES) or []

        if config[ATTR_METHOD] == InterfaceMethod.STATIC and not addresses:
            raise vol.Invalid(
                f"{schema_key}: at least one address is required when method is static"
            )

        if config[ATTR_METHOD] != InterfaceMethod.STATIC and (
            addresses or config.get(ATTR_GATEWAY)
        ):
            # Not supported/configurable via Supervisor today - an externally
            # managed profile with a non-static method plus manual
            # addresses/gateway isn't something we can round-trip (only
            # `static` is serialized back out), see #7110. This also
            # supersedes (and subsumes) the old "gateway requires an
            # address" check below: with `static` required for either field
            # to be set at all, and `static` itself requiring a non-empty
            # `addresses`, a gateway can no longer be supplied without one.
            raise vol.Invalid(
                f"{schema_key}: addresses and gateway are only supported when method is static"
            )

        return config

    return validator


def _validate_wifi_config_v2(config: dict[str, Any]) -> dict[str, Any]:
    """Reject a psk supplied without a matching auth method."""
    if config.get(ATTR_PSK) and config[ATTR_AUTH] != AuthMethod.WPA_PSK:
        raise vol.Invalid(f"{ATTR_PSK} is only valid when {ATTR_AUTH} is wpa-psk")

    return config


_SCHEMA_IPV4_CONFIG_V2 = vol.All(
    vol.Schema(
        {
            vol.Required(ATTR_METHOD): vol.Coerce(InterfaceMethod),
            vol.Optional(ATTR_ADDRESSES, default=list): [vol.Coerce(IPv4Interface)],
            vol.Optional(ATTR_GATEWAY): vol.Any(vol.Coerce(IPv4Address), None),
            vol.Optional(ATTR_ROUTE_METRIC): vol.Any(vol.Coerce(int), None),
            vol.Optional(ATTR_NAMESERVERS, default=list): [vol.Coerce(IPv4Address)],
        }
    ),
    _validate_ip_config_v2(ATTR_IPV4),
)

_SCHEMA_IPV6_CONFIG_V2 = vol.All(
    vol.Schema(
        {
            vol.Required(ATTR_METHOD): vol.Coerce(InterfaceMethod),
            vol.Optional(ATTR_ADDR_GEN_MODE): vol.Coerce(InterfaceAddrGenMode),
            vol.Optional(ATTR_IP6_PRIVACY): vol.Coerce(InterfaceIp6Privacy),
            vol.Optional(ATTR_ADDRESSES, default=list): [vol.Coerce(IPv6Interface)],
            vol.Optional(ATTR_GATEWAY): vol.Any(vol.Coerce(IPv6Address), None),
            vol.Optional(ATTR_ROUTE_METRIC): vol.Any(vol.Coerce(int), None),
            vol.Optional(ATTR_NAMESERVERS, default=list): [vol.Coerce(IPv6Address)],
        }
    ),
    _validate_ip_config_v2(ATTR_IPV6),
)

_SCHEMA_WIFI_CONFIG_V2 = vol.All(
    vol.Schema(
        {
            vol.Required(ATTR_MODE): vol.Coerce(WifiMode),
            vol.Required(ATTR_SSID): vol.All(str, vol.Length(min=1)),
            vol.Required(ATTR_AUTH): vol.Coerce(AuthMethod),
            vol.Optional(ATTR_PSK): str,
            # Read-only marker returned by GET, accepted (and ignored) here so
            # an unchanged `config` round-trips through PUT (R1).
            vol.Optional(ATTR_PSK_SET): vol.Boolean(),
        }
    ),
    _validate_wifi_config_v2,
)


# pylint: disable=no-value-for-parameter
SCHEMA_CONFIG_V2 = vol.Schema(
    {
        vol.Required(ATTR_ENABLED): vol.Boolean(),
        vol.Required(ATTR_IPV4): _SCHEMA_IPV4_CONFIG_V2,
        vol.Required(ATTR_IPV6): _SCHEMA_IPV6_CONFIG_V2,
        vol.Optional(ATTR_WIFI): vol.Any(_SCHEMA_WIFI_CONFIG_V2, None),
        vol.Required(ATTR_MDNS): vol.Coerce(MulticastDnsMode),
        vol.Required(ATTR_LLMNR): vol.Coerce(MulticastDnsMode),
    }
)


def ip4config_struct(config: IpConfig, setting: IpSetting) -> dict[str, Any]:
    """Return a dict with information about IPv4 configuration."""
    return {
        ATTR_METHOD: setting.method,
        ATTR_ADDRESS: [address.with_prefixlen for address in config.address],
        ATTR_NAMESERVERS: [str(address) for address in config.nameservers],
        ATTR_GATEWAY: str(config.gateway) if config.gateway else None,
        ATTR_ROUTE_METRIC: setting.route_metric,
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
        ATTR_ROUTE_METRIC: setting.route_metric,
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
        ATTR_MDNS: interface.mdns,
        ATTR_LLMNR: interface.llmnr,
    }


def interface_state_struct(interface: Interface) -> dict[str, Any]:
    """Return a dict with the observed state of an interface (v2)."""
    return {
        ATTR_CONNECTED: interface.connected,
        ATTR_IPV4: {
            ATTR_ADDRESSES: [
                address.with_prefixlen for address in interface.ipv4.address
            ],
            ATTR_GATEWAY: str(interface.ipv4.gateway)
            if interface.ipv4.gateway
            else None,
            ATTR_NAMESERVERS: [str(address) for address in interface.ipv4.nameservers],
            ATTR_READY: interface.ipv4.ready,
        }
        if interface.ipv4
        else None,
        ATTR_IPV6: {
            ATTR_ADDRESSES: [
                address.with_prefixlen for address in interface.ipv6.address
            ],
            ATTR_GATEWAY: str(interface.ipv6.gateway)
            if interface.ipv6.gateway
            else None,
            ATTR_NAMESERVERS: [str(address) for address in interface.ipv6.nameservers],
            ATTR_READY: interface.ipv6.ready,
        }
        if interface.ipv6
        else None,
        ATTR_WIFI: {
            ATTR_SSID: interface.wifi.active_ssid,
            ATTR_SIGNAL: interface.wifi.signal,
        }
        if interface.wifi
        else None,
    }


def interface_config_struct(resolved: ResolvedInterface) -> dict[str, Any] | None:
    """Return a dict with the desired configuration of an interface (v2).

    Returns `None` if no stored connection profile could be resolved for the
    interface at all (as opposed to v1, which always returns a dummy
    `disabled`/empty config in that case).
    """
    if not resolved.has_profile:
        return None

    interface = resolved.interface
    return {
        ATTR_ENABLED: resolved.enabled,
        ATTR_IPV4: {
            ATTR_METHOD: interface.ipv4setting.method,
            ATTR_ADDRESSES: [
                address.with_prefixlen for address in interface.ipv4setting.address
            ],
            ATTR_GATEWAY: str(interface.ipv4setting.gateway)
            if interface.ipv4setting.gateway
            else None,
            ATTR_ROUTE_METRIC: interface.ipv4setting.route_metric,
            ATTR_NAMESERVERS: [
                str(address) for address in interface.ipv4setting.nameservers
            ],
        }
        if interface.ipv4setting
        else None,
        ATTR_IPV6: {
            ATTR_METHOD: interface.ipv6setting.method,
            ATTR_ADDR_GEN_MODE: interface.ipv6setting.addr_gen_mode,
            ATTR_IP6_PRIVACY: interface.ipv6setting.ip6_privacy,
            ATTR_ADDRESSES: [
                address.with_prefixlen for address in interface.ipv6setting.address
            ],
            ATTR_GATEWAY: str(interface.ipv6setting.gateway)
            if interface.ipv6setting.gateway
            else None,
            ATTR_ROUTE_METRIC: interface.ipv6setting.route_metric,
            ATTR_NAMESERVERS: [
                str(address) for address in interface.ipv6setting.nameservers
            ],
        }
        if interface.ipv6setting
        else None,
        ATTR_WIFI: {
            ATTR_MODE: interface.wifi.mode,
            ATTR_SSID: interface.wifi.ssid,
            ATTR_AUTH: interface.wifi.auth,
            ATTR_PSK_SET: interface.wifi.auth == AuthMethod.WPA_PSK,
        }
        if interface.wifi
        else None,
        ATTR_MDNS: interface.mdns,
        ATTR_LLMNR: interface.llmnr,
    }


def interface_struct_v2(resolved: ResolvedInterface) -> dict[str, Any]:
    """Return a dict with information of an interface for the v2 API."""
    interface = resolved.interface
    return {
        ATTR_NAME: interface.name,
        ATTR_TYPE: interface.type,
        ATTR_MAC: interface.mac,
        ATTR_PATH: interface.path,
        ATTR_PRIMARY: interface.primary,
        ATTR_STATE: interface_state_struct(interface),
        ATTR_CONFIG: interface_config_struct(resolved),
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
    async def info(self, _: web.Request) -> dict[str, Any]:
        """Return network information."""
        return {
            ATTR_INTERFACES: [
                interface_struct(interface)
                for interface in self.sys_host.network.interfaces
            ],
            ATTR_DOCKER: {
                ATTR_INTERFACE: DOCKER_NETWORK,
                ATTR_ADDRESS: str(DOCKER_IPV4_NETWORK_MASK),
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

    async def _get_resolved_interface_v2(self, name: str) -> ResolvedInterface:
        """Get a resolved interface (state+config) by name for the v2 API.

        Unlike `_get_interface()`, this does not support the `default` alias
        (dropped in v2) and excludes VLAN interfaces (not shown in v2 for now).
        """
        try:
            resolved = await self.sys_host.network.get_with_config(name)
        except HostNetworkNotFound:
            raise APINotFound(f"Interface {name} does not exist") from None

        if resolved.interface.type == InterfaceType.VLAN:
            raise APINotFound(f"Interface {name} does not exist") from None

        return resolved

    @api_process
    async def info_v2(self, _: web.Request) -> dict[str, Any]:
        """Return network information (v2)."""
        return {
            ATTR_INTERFACES: [
                interface_struct_v2(resolved)
                for resolved in await self.sys_host.network.interfaces_with_config()
                if resolved.interface.type != InterfaceType.VLAN
            ],
            ATTR_DOCKER: {
                ATTR_INTERFACE: DOCKER_NETWORK,
                ATTR_ADDRESS: str(DOCKER_IPV4_NETWORK_MASK),
                ATTR_GATEWAY: str(self.sys_docker.network.gateway),
                ATTR_DNS: str(self.sys_docker.network.dns),
            },
            ATTR_HOST_INTERNET: self.sys_host.network.connectivity,
            ATTR_SUPERVISOR_INTERNET: self.sys_supervisor.connectivity,
        }

    @api_process
    async def interface_info_v2(self, request: web.Request) -> dict[str, Any]:
        """Return network information for an interface (v2)."""
        resolved = await self._get_resolved_interface_v2(request.match_info[ATTR_NAME])

        return interface_struct_v2(resolved)

    @api_process
    async def update_config_v2(self, request: web.Request) -> dict[str, Any]:
        """Replace the desired configuration of an interface (v2)."""
        resolved = await self._get_resolved_interface_v2(request.match_info[ATTR_NAME])
        interface = resolved.interface

        body = await api_validate(SCHEMA_CONFIG_V2, request)

        if not resolved.has_profile and not body[ATTR_ENABLED]:
            # No stored connection profile exists for this interface at all
            # (GET reports `config: null`), and this PUT wouldn't create one
            # since disabling never activates a new connection - it would
            # just report success while leaving `config: null` unchanged,
            # breaking the full-document replace contract. Creating a
            # profile that starts out disabled isn't a feature we need to
            # support, so reject this combination as an explicit exception
            # to round-tripping for now; revisit with `config_source` (#7110).
            raise APIError(
                f"Interface {interface.name} has no existing configuration; "
                "it cannot be replaced with a disabled one"
            )

        if interface.type == InterfaceType.WIRELESS and body.get(ATTR_WIFI) is None:
            raise APIError(
                f"Interface {interface.name} is wireless and requires a wifi configuration"
            )
        if interface.type != InterfaceType.WIRELESS and body.get(ATTR_WIFI) is not None:
            raise APIError(
                f"Interface {interface.name} is not wireless and does not support a wifi configuration"
            )

        ipv4 = body[ATTR_IPV4]
        interface.ipv4setting = IpSetting(
            method=ipv4[ATTR_METHOD],
            address=ipv4[ATTR_ADDRESSES],
            gateway=ipv4.get(ATTR_GATEWAY),
            route_metric=ipv4.get(ATTR_ROUTE_METRIC),
            nameservers=ipv4[ATTR_NAMESERVERS],
        )

        ipv6 = body[ATTR_IPV6]
        interface.ipv6setting = Ip6Setting(
            method=ipv6[ATTR_METHOD],
            addr_gen_mode=ipv6.get(ATTR_ADDR_GEN_MODE, InterfaceAddrGenMode.DEFAULT),
            ip6_privacy=ipv6.get(ATTR_IP6_PRIVACY, InterfaceIp6Privacy.DEFAULT),
            address=ipv6[ATTR_ADDRESSES],
            gateway=ipv6.get(ATTR_GATEWAY),
            route_metric=ipv6.get(ATTR_ROUTE_METRIC),
            nameservers=ipv6[ATTR_NAMESERVERS],
        )

        if body.get(ATTR_WIFI) is not None:
            wifi = body[ATTR_WIFI]
            interface.wifi = WifiConfig(
                mode=wifi[ATTR_MODE],
                ssid=wifi[ATTR_SSID],
                auth=wifi[ATTR_AUTH],
                psk=wifi.get(ATTR_PSK),
                signal=None,
            )

        interface.enabled = body[ATTR_ENABLED]
        interface.mdns = body[ATTR_MDNS]
        interface.llmnr = body[ATTR_LLMNR]

        await asyncio.shield(self.sys_host.network.apply_changes_v2(interface))

        updated = await self.sys_host.network.get_with_config(interface.name)
        return interface_struct_v2(updated)

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
                    route_metric=config.get(ATTR_ROUTE_METRIC),
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
                    route_metric=config.get(ATTR_ROUTE_METRIC),
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
            elif key == ATTR_MDNS:
                interface.mdns = config
            elif key == ATTR_LLMNR:
                interface.llmnr = config

        await asyncio.shield(self.sys_host.network.apply_changes(interface))

    @api_process
    def reload(self, _: web.Request) -> Awaitable[None]:
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

        mdns_mode = MulticastDnsMode.DEFAULT
        llmnr_mode = MulticastDnsMode.DEFAULT

        if ATTR_MDNS in body:
            mdns_mode = body[ATTR_MDNS]

        if ATTR_LLMNR in body:
            llmnr_mode = body[ATTR_LLMNR]

        ipv4_setting = None
        if ATTR_IPV4 in body:
            ipv4_setting = IpSetting(
                method=body[ATTR_IPV4].get(ATTR_METHOD, InterfaceMethod.AUTO),
                address=body[ATTR_IPV4].get(ATTR_ADDRESS, []),
                gateway=body[ATTR_IPV4].get(ATTR_GATEWAY),
                route_metric=body[ATTR_IPV4].get(ATTR_ROUTE_METRIC),
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
                gateway=body[ATTR_IPV6].get(ATTR_GATEWAY),
                route_metric=body[ATTR_IPV6].get(ATTR_ROUTE_METRIC),
                nameservers=body[ATTR_IPV6].get(ATTR_NAMESERVERS, []),
            )

        vlan_interface = Interface(
            f"{interface.name}.{vlan}",
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
            mdns=mdns_mode,
            llmnr=llmnr_mode,
        )
        await asyncio.shield(self.sys_host.network.create_vlan(vlan_interface))
