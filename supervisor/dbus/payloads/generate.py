"""Payload generators for DBUS communication."""
from __future__ import annotations

from ipaddress import IPv4Address, IPv6Address
from pathlib import Path
import socket
from typing import TYPE_CHECKING, Optional
from uuid import uuid4

import jinja2

from ...host.const import InterfaceType

if TYPE_CHECKING:
    from ...host.network import Interface


INTERFACE_UPDATE_TEMPLATE: Path = (
    Path(__file__).parents[2].joinpath("dbus/payloads/interface_update.tmpl")
)


def interface_update_payload(
    interface: Interface, name: Optional[str] = None, uuid: Optional[str] = None
) -> str:
    """Generate a payload for network interface update."""
    env = jinja2.Environment()

    def ipv4_to_int(ip_address: IPv4Address) -> int:
        """Convert an ipv4 to an int."""
        return socket.htonl(int(ip_address))

    def ipv6_to_byte(ip_address: IPv6Address) -> str:
        """Convert an ipv6 to an byte array."""
        return (
            f'[byte {", ".join("0x{:02x}".format(val) for val in ip_address.packed)}]'
        )

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
