"""Payload generators for DBUS communication."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING, cast
from uuid import uuid4

from dbus_fast import Variant

from ....host.configuration import Ip6Setting, IpSetting, VlanConfig
from ....host.const import (
    InterfaceAddrGenMode,
    InterfaceIp6Privacy,
    InterfaceMethod,
    InterfaceType,
)
from .. import NetworkManager
from . import (
    CONF_ATTR_802_ETHERNET,
    CONF_ATTR_802_ETHERNET_ASSIGNED_MAC,
    CONF_ATTR_802_WIRELESS,
    CONF_ATTR_802_WIRELESS_ASSIGNED_MAC,
    CONF_ATTR_802_WIRELESS_MODE,
    CONF_ATTR_802_WIRELESS_POWERSAVE,
    CONF_ATTR_802_WIRELESS_SECURITY,
    CONF_ATTR_802_WIRELESS_SECURITY_AUTH_ALG,
    CONF_ATTR_802_WIRELESS_SECURITY_KEY_MGMT,
    CONF_ATTR_802_WIRELESS_SECURITY_PSK,
    CONF_ATTR_802_WIRELESS_SSID,
    CONF_ATTR_CONNECTION,
    CONF_ATTR_CONNECTION_AUTOCONNECT,
    CONF_ATTR_CONNECTION_ID,
    CONF_ATTR_CONNECTION_LLMNR,
    CONF_ATTR_CONNECTION_MDNS,
    CONF_ATTR_CONNECTION_TYPE,
    CONF_ATTR_CONNECTION_UUID,
    CONF_ATTR_IPV4,
    CONF_ATTR_IPV4_ADDRESS_DATA,
    CONF_ATTR_IPV4_DNS,
    CONF_ATTR_IPV4_GATEWAY,
    CONF_ATTR_IPV4_METHOD,
    CONF_ATTR_IPV6,
    CONF_ATTR_IPV6_ADDR_GEN_MODE,
    CONF_ATTR_IPV6_ADDRESS_DATA,
    CONF_ATTR_IPV6_DNS,
    CONF_ATTR_IPV6_GATEWAY,
    CONF_ATTR_IPV6_METHOD,
    CONF_ATTR_IPV6_PRIVACY,
    CONF_ATTR_MATCH,
    CONF_ATTR_MATCH_PATH,
    CONF_ATTR_VLAN,
    CONF_ATTR_VLAN_ID,
    CONF_ATTR_VLAN_PARENT,
)

if TYPE_CHECKING:
    from ....host.configuration import Interface


def _get_ipv4_connection_settings(ipv4setting: IpSetting | None) -> dict:
    ipv4 = {}
    if not ipv4setting or ipv4setting.method == InterfaceMethod.AUTO:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "auto")
    elif ipv4setting.method == InterfaceMethod.DISABLED:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "disabled")
    elif ipv4setting.method == InterfaceMethod.STATIC:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "manual")

        address_data = []
        for address in ipv4setting.address:
            address_data.append(
                {
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
                }
            )

        ipv4[CONF_ATTR_IPV4_ADDRESS_DATA] = Variant("aa{sv}", address_data)
        if ipv4setting.gateway:
            ipv4[CONF_ATTR_IPV4_GATEWAY] = Variant("s", str(ipv4setting.gateway))
    else:
        raise RuntimeError("Invalid IPv4 InterfaceMethod")

    if (
        ipv4setting
        and ipv4setting.nameservers
        and ipv4setting.method
        in (
            InterfaceMethod.AUTO,
            InterfaceMethod.STATIC,
        )
    ):
        nameservers = ipv4setting.nameservers if ipv4setting else []
        ipv4[CONF_ATTR_IPV4_DNS] = Variant(
            "au",
            [socket.htonl(int(ip_address)) for ip_address in nameservers],
        )

    return ipv4


def _get_ipv6_connection_settings(
    ipv6setting: Ip6Setting | None, support_addr_gen_mode_defaults: bool = False
) -> dict:
    ipv6 = {}
    if not ipv6setting or ipv6setting.method == InterfaceMethod.AUTO:
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "auto")
        if ipv6setting:
            if ipv6setting.addr_gen_mode == InterfaceAddrGenMode.EUI64:
                ipv6[CONF_ATTR_IPV6_ADDR_GEN_MODE] = Variant("i", 0)
            elif (
                not support_addr_gen_mode_defaults
                or ipv6setting.addr_gen_mode == InterfaceAddrGenMode.STABLE_PRIVACY
            ):
                ipv6[CONF_ATTR_IPV6_ADDR_GEN_MODE] = Variant("i", 1)
            elif ipv6setting.addr_gen_mode == InterfaceAddrGenMode.DEFAULT_OR_EUI64:
                ipv6[CONF_ATTR_IPV6_ADDR_GEN_MODE] = Variant("i", 2)
            else:
                ipv6[CONF_ATTR_IPV6_ADDR_GEN_MODE] = Variant("i", 3)
            if ipv6setting.ip6_privacy == InterfaceIp6Privacy.DISABLED:
                ipv6[CONF_ATTR_IPV6_PRIVACY] = Variant("i", 0)
            elif ipv6setting.ip6_privacy == InterfaceIp6Privacy.ENABLED_PREFER_PUBLIC:
                ipv6[CONF_ATTR_IPV6_PRIVACY] = Variant("i", 1)
            elif ipv6setting.ip6_privacy == InterfaceIp6Privacy.ENABLED:
                ipv6[CONF_ATTR_IPV6_PRIVACY] = Variant("i", 2)
            else:
                ipv6[CONF_ATTR_IPV6_PRIVACY] = Variant("i", -1)
    elif ipv6setting.method == InterfaceMethod.DISABLED:
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "link-local")
    elif ipv6setting.method == InterfaceMethod.STATIC:
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "manual")

        address_data = []
        for address in ipv6setting.address:
            address_data.append(
                {
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
                }
            )

        ipv6[CONF_ATTR_IPV6_ADDRESS_DATA] = Variant("aa{sv}", address_data)
        if ipv6setting.gateway:
            ipv6[CONF_ATTR_IPV6_GATEWAY] = Variant("s", str(ipv6setting.gateway))
    else:
        raise RuntimeError("Invalid IPv6 InterfaceMethod")

    if (
        ipv6setting
        and ipv6setting.nameservers
        and ipv6setting.method
        in (
            InterfaceMethod.AUTO,
            InterfaceMethod.STATIC,
        )
    ):
        nameservers = ipv6setting.nameservers if ipv6setting else []
        ipv6[CONF_ATTR_IPV6_DNS] = Variant(
            "aay",
            [ip_address.packed for ip_address in nameservers],
        )
    return ipv6


def get_connection_from_interface(
    interface: Interface,
    network_manager: NetworkManager,
    name: str | None = None,
    uuid: str | None = None,
) -> dict[str, dict[str, Variant]]:
    """Generate message argument for network interface update."""
    # Simple input check to ensure it is safe to cast this for type checker
    if interface.type == InterfaceType.VLAN and not interface.vlan:
        raise ValueError("Interface has type vlan but no vlan config!")

    # Generate/Update ID/name
    if not name or not name.startswith("Supervisor"):
        name = f"Supervisor {interface.name}"
        if interface.type == InterfaceType.VLAN:
            name = f"{name}.{cast(VlanConfig, interface.vlan).id}"

    if interface.type == InterfaceType.ETHERNET:
        iftype = "802-3-ethernet"
    elif interface.type == InterfaceType.WIRELESS:
        iftype = "802-11-wireless"
    else:
        iftype = interface.type

    # Generate UUID
    if not uuid:
        uuid = str(uuid4())

    conn: dict[str, dict[str, Variant]] = {
        CONF_ATTR_CONNECTION: {
            CONF_ATTR_CONNECTION_ID: Variant("s", name),
            CONF_ATTR_CONNECTION_UUID: Variant("s", uuid),
            CONF_ATTR_CONNECTION_TYPE: Variant("s", iftype),
            CONF_ATTR_CONNECTION_LLMNR: Variant("i", 2),
            CONF_ATTR_CONNECTION_MDNS: Variant("i", 2),
            CONF_ATTR_CONNECTION_AUTOCONNECT: Variant("b", True),
        },
    }

    if interface.type != InterfaceType.VLAN:
        if interface.path:
            conn[CONF_ATTR_MATCH] = {
                CONF_ATTR_MATCH_PATH: Variant("as", [interface.path])
            }
        else:
            conn[CONF_ATTR_CONNECTION]["interface-name"] = Variant("s", interface.name)

    conn[CONF_ATTR_IPV4] = _get_ipv4_connection_settings(interface.ipv4setting)

    conn[CONF_ATTR_IPV6] = _get_ipv6_connection_settings(
        interface.ipv6setting, network_manager.version >= "1.40.0"
    )

    if interface.type == InterfaceType.ETHERNET:
        conn[CONF_ATTR_802_ETHERNET] = {
            CONF_ATTR_802_ETHERNET_ASSIGNED_MAC: Variant("s", "preserve")
        }
    elif interface.type == "vlan":
        parent = cast(VlanConfig, interface.vlan).interface
        if parent in network_manager and (
            parent_connection := network_manager.get(parent).connection
        ):
            parent = parent_connection.uuid

        conn[CONF_ATTR_VLAN] = {
            CONF_ATTR_VLAN_ID: Variant("u", cast(VlanConfig, interface.vlan).id),
            CONF_ATTR_VLAN_PARENT: Variant("s", parent),
        }
    elif interface.type == InterfaceType.WIRELESS:
        wireless = {
            CONF_ATTR_802_WIRELESS_ASSIGNED_MAC: Variant("s", "preserve"),
            CONF_ATTR_802_WIRELESS_MODE: Variant("s", "infrastructure"),
            CONF_ATTR_802_WIRELESS_POWERSAVE: Variant("i", 1),
        }
        if interface.wifi and interface.wifi.ssid:
            wireless[CONF_ATTR_802_WIRELESS_SSID] = Variant(
                "ay", interface.wifi.ssid.encode("UTF-8")
            )

        conn[CONF_ATTR_802_WIRELESS] = wireless

        if interface.wifi and interface.wifi.auth != "open":
            wireless["security"] = Variant("s", CONF_ATTR_802_WIRELESS_SECURITY)
            wireless_security = {}
            if interface.wifi.auth == "wep":
                wireless_security[CONF_ATTR_802_WIRELESS_SECURITY_AUTH_ALG] = Variant(
                    "s", "open"
                )
                wireless_security[CONF_ATTR_802_WIRELESS_SECURITY_KEY_MGMT] = Variant(
                    "s", "none"
                )
            elif interface.wifi.auth == "wpa-psk":
                wireless_security[CONF_ATTR_802_WIRELESS_SECURITY_AUTH_ALG] = Variant(
                    "s", "open"
                )
                wireless_security[CONF_ATTR_802_WIRELESS_SECURITY_KEY_MGMT] = Variant(
                    "s", "wpa-psk"
                )

            if interface.wifi.psk:
                wireless_security[CONF_ATTR_802_WIRELESS_SECURITY_PSK] = Variant(
                    "s", interface.wifi.psk
                )
            conn[CONF_ATTR_802_WIRELESS_SECURITY] = wireless_security

    return conn
