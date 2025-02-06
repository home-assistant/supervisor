"""Payload generators for DBUS communication."""

from __future__ import annotations

import socket
from typing import TYPE_CHECKING
from uuid import uuid4

from dbus_fast import Variant

from ....host.const import InterfaceMethod, InterfaceType
from .. import NetworkManager
from . import (
    CONF_ATTR_802_ETHERNET,
    CONF_ATTR_802_ETHERNET_ASSIGNED_MAC,
    CONF_ATTR_802_WIRELESS,
    CONF_ATTR_802_WIRELESS_ASSIGNED_MAC,
    CONF_ATTR_802_WIRELESS_BAND,
    CONF_ATTR_802_WIRELESS_CHANNEL,
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
    CONF_ATTR_IPV6_ADDRESS_DATA,
    CONF_ATTR_IPV6_DNS,
    CONF_ATTR_IPV6_GATEWAY,
    CONF_ATTR_IPV6_METHOD,
    CONF_ATTR_MATCH,
    CONF_ATTR_MATCH_PATH,
    CONF_ATTR_VLAN,
    CONF_ATTR_VLAN_ID,
    CONF_ATTR_VLAN_PARENT,
)

if TYPE_CHECKING:
    from ....host.configuration import Interface


def _get_address_data(ipv4setting) -> Variant:
    address_data = []
    for address in ipv4setting.address:
        address_data.append(
            {
                "address": Variant("s", str(address.ip)),
                "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
            }
        )

    return Variant("aa{sv}", address_data)


def _get_ipv4_connection_settings(ipv4setting) -> dict:
    ipv4 = {}
    if not ipv4setting or ipv4setting.method == InterfaceMethod.AUTO:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "auto")
    elif ipv4setting.method == InterfaceMethod.DISABLED:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "disabled")
    elif ipv4setting.method == InterfaceMethod.STATIC:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "manual")
        ipv4[CONF_ATTR_IPV4_ADDRESS_DATA] = _get_address_data(ipv4setting)
        if ipv4setting.gateway:
            ipv4[CONF_ATTR_IPV4_GATEWAY] = Variant("s", str(ipv4setting.gateway))
    elif ipv4setting.method == InterfaceMethod.SHARED:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "shared")
        ipv4[CONF_ATTR_IPV4_ADDRESS_DATA] = _get_address_data(ipv4setting)
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


def _get_ipv6_connection_settings(ipv6setting) -> dict:
    ipv6 = {}
    if not ipv6setting or ipv6setting.method == InterfaceMethod.AUTO:
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "auto")
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

    # Generate/Update ID/name
    if not name or not name.startswith("Supervisor"):
        name = f"Supervisor {interface.name}"
        if interface.type == InterfaceType.VLAN:
            name = f"{name}.{interface.vlan.id}"

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

    conn[CONF_ATTR_IPV6] = _get_ipv6_connection_settings(interface.ipv6setting)

    if interface.type == InterfaceType.ETHERNET:
        conn[CONF_ATTR_802_ETHERNET] = {
            CONF_ATTR_802_ETHERNET_ASSIGNED_MAC: Variant("s", "preserve")
        }
    elif interface.type == "vlan":
        parent = interface.vlan.interface
        if parent in network_manager and (
            parent_connection := network_manager.get(parent).connection
        ):
            parent = parent_connection.uuid

        conn[CONF_ATTR_VLAN] = {
            CONF_ATTR_VLAN_ID: Variant("u", interface.vlan.id),
            CONF_ATTR_VLAN_PARENT: Variant("s", parent),
        }
    elif interface.type == InterfaceType.WIRELESS:
        wireless = {
            CONF_ATTR_802_WIRELESS_ASSIGNED_MAC: Variant("s", "preserve"),
            CONF_ATTR_802_WIRELESS_MODE: Variant(
                "s", (interface.wifi and interface.wifi.mode) or "infrastructure"
            ),
            CONF_ATTR_802_WIRELESS_POWERSAVE: Variant("i", 1),
        }
        if interface.wifi and interface.wifi.ssid:
            wireless[CONF_ATTR_802_WIRELESS_SSID] = Variant(
                "ay", interface.wifi.ssid.encode("UTF-8")
            )
        if interface.wifi and interface.wifi.band:
            wireless[CONF_ATTR_802_WIRELESS_BAND] = Variant("s", interface.wifi.band)
        if interface.wifi and interface.wifi.channel:
            wireless[CONF_ATTR_802_WIRELESS_CHANNEL] = Variant(
                "u", interface.wifi.channel
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
