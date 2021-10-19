"""Payload generators for DBUS communication."""
from __future__ import annotations

import socket
from typing import TYPE_CHECKING, Any
from uuid import uuid4

from dbus_next.signature import Variant

from . import (
    ATTR_ASSIGNED_MAC,
    CONF_ATTR_802_ETHERNET,
    CONF_ATTR_802_WIRELESS,
    CONF_ATTR_802_WIRELESS_SECURITY,
    CONF_ATTR_CONNECTION,
    CONF_ATTR_IPV4,
    CONF_ATTR_IPV6,
    CONF_ATTR_VLAN,
)
from ....host.const import InterfaceMethod, InterfaceType

if TYPE_CHECKING:
    from ....host.network import Interface


def get_connection_from_interface(
    interface: Interface, name: str | None = None, uuid: str | None = None
) -> Any:
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
        iftype = interface.type.value

    # Generate UUID
    if not uuid:
        uuid = str(uuid4())

    connection = {
        "id": Variant("s", name),
        "type": Variant("s", iftype),
        "uuid": Variant("s", uuid),
        "llmnr": Variant("i", 2),
        "mdns": Variant("i", 2),
    }

    if interface.type != InterfaceType.VLAN:
        connection["interface-name"] = Variant("s", interface.name)

    conn = {}
    conn[CONF_ATTR_CONNECTION] = connection

    ipv4 = {}
    if not interface.ipv4 or interface.ipv4.method == InterfaceMethod.AUTO:
        ipv4["method"] = Variant("s", "auto")
    elif interface.ipv4.method == InterfaceMethod.DISABLED:
        ipv4["method"] = Variant("s", "disabled")
    else:
        ipv4["method"] = Variant("s", "manual")
        ipv4["dns"] = Variant(
            "au",
            [
                socket.htonl(int(ip_address))
                for ip_address in interface.ipv4.nameservers
            ],
        )

        adressdata = []
        for address in interface.ipv4.address:
            adressdata.append(
                {
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
                }
            )

        ipv4["address-data"] = Variant("aa{sv}", adressdata)
        ipv4["gateway"] = Variant("s", str(interface.ipv4.gateway))

    conn[CONF_ATTR_IPV4] = ipv4

    ipv6 = {}
    if not interface.ipv6 or interface.ipv6.method == InterfaceMethod.AUTO:
        ipv6["method"] = Variant("s", "auto")
    elif interface.ipv6.method == InterfaceMethod.DISABLED:
        ipv6["method"] = Variant("s", "disabled")
    else:
        ipv6["method"] = Variant("s", "manual")
        ipv6["dns"] = Variant(
            "aay", [ip_address.packed for ip_address in interface.ipv6.nameservers]
        )

        adressdata = []
        for address in interface.ipv6.address:
            if address.with_prefixlen.startswith("fe80::"):
                continue
            adressdata.append(
                {
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1])),
                }
            )

        ipv6["address-data"] = Variant("(a{sv})", adressdata)
        ipv6["gateway"] = Variant("s", str(interface.ipv6.gateway))

    conn[CONF_ATTR_IPV6] = ipv6

    if interface.type == InterfaceType.ETHERNET:
        conn[CONF_ATTR_802_ETHERNET] = {ATTR_ASSIGNED_MAC: Variant("s", "preserve")}
    elif interface.type == "vlan":
        conn[CONF_ATTR_VLAN] = {
            "id": Variant("u", interface.vlan.id),
            "parent": Variant("s", interface.vlan.interface),
        }
    elif interface.type == InterfaceType.WIRELESS:
        wireless = {
            ATTR_ASSIGNED_MAC: Variant("s", "preserve"),
            "ssid": Variant("ay", interface.wifi.ssid.encode("UTF-8")),
            "mode": Variant("s", "infrastructure"),
            "powersave": Variant("i", 1),
        }
        conn[CONF_ATTR_802_WIRELESS] = wireless

        if interface.wifi.auth != "open":
            wireless["security"] = Variant("s", CONF_ATTR_802_WIRELESS_SECURITY)
            wireless_security = {}
            if interface.wifi.auth == "wep":
                wireless_security["auth-alg"] = Variant("s", "none")
                wireless_security["key-mgmt"] = Variant("s", "open")
            elif interface.wifi.auth == "wpa-psk":
                wireless_security["auth-alg"] = Variant("s", "open")
                wireless_security["key-mgmt"] = Variant("s", "wpa-psk")

            if interface.wifi.psk:
                wireless_security["psk"] = Variant("s", interface.wifi.psk)
            conn[CONF_ATTR_802_WIRELESS_SECURITY] = wireless_security

    return conn
