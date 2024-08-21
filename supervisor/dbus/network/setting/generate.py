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

    ipv4 = {}
    if (
        not interface.ipv4setting
        or interface.ipv4setting.method == InterfaceMethod.AUTO
    ):
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "auto")
    elif interface.ipv4setting.method == InterfaceMethod.DISABLED:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "disabled")
    else:
        ipv4[CONF_ATTR_IPV4_METHOD] = Variant("s", "manual")
        ipv4[CONF_ATTR_IPV4_DNS] = Variant(
            "au",
            [
                socket.htonl(int(ip_address))
                for ip_address in interface.ipv4setting.nameservers
            ],
        )

        address_data = []
        for address in interface.ipv4setting.address:
            address_data.append(
                {
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
                }
            )

        ipv4[CONF_ATTR_IPV4_ADDRESS_DATA] = Variant("aa{sv}", address_data)
        ipv4[CONF_ATTR_IPV4_GATEWAY] = Variant("s", str(interface.ipv4setting.gateway))

    conn[CONF_ATTR_IPV4] = ipv4

    ipv6 = {}
    if (
        not interface.ipv6setting
        or interface.ipv6setting.method == InterfaceMethod.AUTO
    ):
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "auto")
    elif interface.ipv6setting.method == InterfaceMethod.DISABLED:
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "link-local")
    else:
        ipv6[CONF_ATTR_IPV6_METHOD] = Variant("s", "manual")
        ipv6[CONF_ATTR_IPV6_DNS] = Variant(
            "aay",
            [ip_address.packed for ip_address in interface.ipv6setting.nameservers],
        )

        address_data = []
        for address in interface.ipv6setting.address:
            address_data.append(
                {
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
                }
            )

        ipv6[CONF_ATTR_IPV6_ADDRESS_DATA] = Variant("aa{sv}", address_data)
        ipv6[CONF_ATTR_IPV6_GATEWAY] = Variant("s", str(interface.ipv6setting.gateway))

    conn[CONF_ATTR_IPV6] = ipv6

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
            CONF_ATTR_802_WIRELESS_SSID: Variant(
                "ay", interface.wifi.ssid.encode("UTF-8")
            ),
            CONF_ATTR_802_WIRELESS_MODE: Variant("s", "infrastructure"),
            CONF_ATTR_802_WIRELESS_POWERSAVE: Variant("i", 1),
        }
        conn[CONF_ATTR_802_WIRELESS] = wireless

        if interface.wifi.auth != "open":
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
