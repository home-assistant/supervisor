"""Payload generators for DBUS communication."""
from __future__ import annotations

from ipaddress import IPv4Address, IPv6Address, ip_address
from pathlib import Path
from re import split
import socket
from typing import TYPE_CHECKING, Any
from uuid import uuid4
import dbussy

import jinja2

from ...host.const import InterfaceType

if TYPE_CHECKING:
    from ...host.network import Interface


INTERFACE_UPDATE_TEMPLATE: Path = (
    Path(__file__).parents[2].joinpath("dbus/payloads/interface_update.tmpl")
)

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
        "id": (dbussy.DBUS.Signature("s"), name),
        "interface-name": (dbussy.DBUS.Signature("s"), interface.name),
        "type": (dbussy.DBUS.Signature("s"), type),
        "uuid": (dbussy.DBUS.Signature("s"), uuid),
        "llmnr": (dbussy.DBUS.Signature("i"), 2),
        "mdns": (dbussy.DBUS.Signature("i"), 2)
    }

    conn = {}
    conn["connection"] = connection

    ipv4 = { }
    if interface.ipv4.method == "auto":
        ipv4["method"] = (dbussy.DBUS.Signature("s"), "auto")
    elif interface.ipv4.method == "disabled":
        ipv4["method"] = (dbussy.DBUS.Signature("s"), "disabled")
    else:
        ipv4["method"] = (dbussy.DBUS.Signature("s"), "manual")
        ipv4["dns"] = (dbussy.DBUS.Signature("au"), [ socket.htonl(int(ip_address)) for ip_address in interface.ipv4.nameservers ])

        adressdata = []
        for address in interface.ipv4.address:
             adressdata.append({
                    "address": (dbussy.DBUS.Signature("s"), str(address.ip)),
                    "prefix": (dbussy.DBUS.Signature("u"), int(address.with_prefixlen.split("/")[-1]))
                })

        ipv4["address-data"] = (dbussy.DBUS.Signature("(a{sv})"), adressdata)
        ipv4["gateway"] = (dbussy.DBUS.Signature("s"), str(interface.ipv4.gateway))

    conn["ipv4"] = ipv4

    ipv6 = {}
    if interface.ipv6.method == "auto":
        ipv6["method"] = (dbussy.DBUS.Signature("s"), "auto")
    elif interface.ipv6.method == "disabled":
        ipv6["method"] = (dbussy.DBUS.Signature("s"), "disabled")
    else:
        ipv6["method"] = (dbussy.DBUS.Signature("s"), "manual")
        ipv6["dns"] = (dbussy.DBUS.Signature("aay"), [ ip_address.packed for ip_address in interface.ipv6.nameservers ])

        adressdata = []
        for address in interface.ipv6.address:
            if address.with_prefixlen.startswith("fe80::"):
                continue
            adressdata.append({
                    "address": (dbussy.DBUS.Signature("s"), str(address.ip)),
                    "prefix": (dbussy.DBUS.Signature("u"), int(address.with_prefixlen.split("/")[-1]))
                })

        ipv4["address-data"] = (dbussy.DBUS.Signature("(a{sv})"), adressdata)
        ipv4["gateway"] = (dbussy.DBUS.Signature("s"), str(interface.ipv6.gateway))

    conn["ipv6"] = ipv6

    if interface.type == "ethernet":
        conn["802-3-ethernet"] = {
            'assigned-mac-address': (dbussy.DBUS.Signature("s"), "preserve")
        }
    elif interface.type == "vlan":
        conn["vlan"] = {
            'id': (dbussy.DBUS.Signature("u"), interface.vlan.id),
            'parent': (dbussy.DBUS.Signature("s"), interface.vlan.interface)
        }
    elif interface.type == "wireless":
        wireless = {
            "assigned-mac-address": (dbussy.DBUS.Signature("s"), "preserve"),
            "ssid": (dbussy.DBUS.Signature("ay"), interface.wifi.ssid.encode("UTF-8")),
            "mode": (dbussy.DBUS.Signature("s"), 'infrastructure'),
            "powersave": (dbussy.DBUS.Signature("i"), 1),
        }
        conn["802-11-wireless"] = wireless

        if interface.wifi.auth != "open":
            wireless["security"] = (dbussy.DBUS.Signature("s"), '802-11-wireless-security')
            wireless_security = { }
            if interface.wifi.auth == "wep":
                wireless_security["auth-alg"] = (dbussy.DBUS.Signature("s"), 'none')
                wireless_security["key-mgmt"] = (dbussy.DBUS.Signature("s"), 'open')
            elif interface.wifi.auth == "wpa-psk":
                wireless_security["auth-alg"] = (dbussy.DBUS.Signature("s"), 'open')
                wireless_security["key-mgmt"] = (dbussy.DBUS.Signature("s"), 'wpa-psk')

            if interface.wifi.psk:
                wireless_security["psk"] = (dbussy.DBUS.Signature("s"), interface.wifi.psk)
            conn["802-11-wireless-security"] = wireless_security

    return conn

def interface_update_payload(
    interface: Interface, name: str | None = None, uuid: str | None = None
) -> str:
    """Generate a payload for network interface update."""
    env = jinja2.Environment()

    def ipv4_to_int(ip_address: IPv4Address) -> int:
        """Convert an ipv4 to an int."""
        return socket.htonl(int(ip_address))

    def ipv6_to_byte(ip_address: IPv6Address) -> str:
        """Convert an ipv6 to an byte array."""
        return f'[byte {", ".join(f"0x{val:02x}" for val in ip_address.packed)}]'

    # Init template
    env.filters["ipv4_to_int"] = ipv4_to_int
    env.filters["ipv6_to_byte"] = ipv6_to_byte
    template: jinja2.Template = env.from_string(INTERFACE_UPDATE_TEMPLATE.read_text())

    # Generate UUID
    if not uuid:
        uuid = str(uuid4())

    # Generate/Update ID/name
    if not name or not name.startswith("Supervisor"):
        name = f"Supervisor {interface.name}"
    if interface.type == InterfaceType.VLAN:
        name = f"{name}.{interface.vlan.id}"

    # Fix SSID
    if interface.wifi:
        interface.wifi.ssid = ", ".join(
            [f"0x{x}" for x in interface.wifi.ssid.encode().hex(",").split(",")]
        )

    return template.render(interface=interface, name=name, uuid=uuid)
