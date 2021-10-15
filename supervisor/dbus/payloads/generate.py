"""Payload generators for DBUS communication."""
from __future__ import annotations

import socket
from typing import TYPE_CHECKING, Any
from uuid import uuid4
from dbus_next.signature import Variant

from ...host.const import InterfaceType

if TYPE_CHECKING:
    from ...host.network import Interface

def get_connection_from_interface(interface: Interface, name: str | None = None, uuid: str | None = None
) -> Any:
    # Generate/Update ID/name
    if not name or not name.startswith("Supervisor"):
        name = f"Supervisor {interface.name}"
    if interface.type == InterfaceType.VLAN:
        name = f"{name}.{interface.vlan.id}"

    if interface.type == "ethernet":
        type = "802-3-ethernet"
    elif interface.type == "wireless":
        type = "802-11-wireless"
    else:
        type = interface.type.value

    # Generate UUID
    if not uuid:
        uuid = str(uuid4())

    connection = {
        "id": Variant("s", name),
        "interface-name": Variant("s", interface.name),
        "type": Variant("s", type),
        "uuid": Variant("s", uuid),
        "llmnr": Variant("i", 2),
        "mdns": Variant("i", 2)
    }

    conn = {}
    conn["connection"] = connection

    ipv4 = { }
    if interface.ipv4.method == "auto":
        ipv4["method"] = Variant("s", "auto")
    elif interface.ipv4.method == "disabled":
        ipv4["method"] = Variant("s", "disabled")
    else:
        ipv4["method"] = Variant("s", "manual")
        ipv4["dns"] = Variant("au", [ socket.htonl(int(ip_address)) for ip_address in interface.ipv4.nameservers ])

        adressdata = []
        for address in interface.ipv4.address:
             adressdata.append({
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1]))
                })

        ipv4["address-data"] = Variant("aa{sv}", adressdata)
        ipv4["gateway"] = Variant("s", str(interface.ipv4.gateway))

    conn["ipv4"] = ipv4

    ipv6 = {}
    if interface.ipv6.method == "auto":
        ipv6["method"] = Variant("s", "auto")
    elif interface.ipv6.method == "disabled":
        ipv6["method"] = Variant("s", "disabled")
    else:
        ipv6["method"] = Variant("s", "manual")
        ipv6["dns"] = Variant("aay", [ ip_address.packed for ip_address in interface.ipv6.nameservers ])

        adressdata = []
        for address in interface.ipv6.address:
            if address.with_prefixlen.startswith("fe80::"):
                continue
            adressdata.append({
                    "address": Variant("s", str(address.ip)),
                    "prefix": Variant("u", int(address.with_prefixlen.split("/")[-1]))
                })

        ipv4["address-data"] = Variant("(a{sv})", adressdata)
        ipv4["gateway"] = Variant("s", str(interface.ipv6.gateway))

    conn["ipv6"] = ipv6

    if interface.type == "ethernet":
        conn["802-3-ethernet"] = {
            'assigned-mac-address': Variant("s", "preserve")
        }
    elif interface.type == "vlan":
        conn["vlan"] = {
            'id': Variant("u", interface.vlan.id),
            'parent': Variant("s", interface.vlan.interface)
        }
    elif interface.type == "wireless":
        wireless = {
            "assigned-mac-address": Variant("s", "preserve"),
            "ssid": Variant("ay", interface.wifi.ssid.encode("UTF-8")),
            "mode": Variant("s", 'infrastructure'),
            "powersave": Variant("i", 1),
        }
        conn["802-11-wireless"] = wireless

        if interface.wifi.auth != "open":
            wireless["security"] = Variant("s", '802-11-wireless-security')
            wireless_security = { }
            if interface.wifi.auth == "wep":
                wireless_security["auth-alg"] = Variant("s", 'none')
                wireless_security["key-mgmt"] = Variant("s", 'open')
            elif interface.wifi.auth == "wpa-psk":
                wireless_security["auth-alg"] = Variant("s", 'open')
                wireless_security["key-mgmt"] = Variant("s", 'wpa-psk')

            if interface.wifi.psk:
                wireless_security["psk"] = Variant("s", interface.wifi.psk)
            conn["802-11-wireless-security"] = wireless_security

    return conn
