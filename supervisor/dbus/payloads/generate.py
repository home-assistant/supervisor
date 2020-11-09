"""Payload generators for DBUS communication."""
from __future__ import annotations

from pathlib import Path
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
    template = jinja2.Template(INTERFACE_UPDATE_TEMPLATE.read_text())

    # Generate UUID
    if not uuid:
        uuid = str(uuid4())

    # Generate ID/name
    if not name and interface.type != InterfaceType.VLAN:
        name = f"Supervisor {interface.name} - {interface.type!s}"
    elif not name:
        name = f"Supervisor {interface.name}.{interface.vlan.id}"

    # Fix SSID
    if interface.wifi:
        interface.wifi.ssid = ", ".join(
            [f"0x{x}" for x in interface.wifi.ssid.encode().hex(",").split(",")]
        )

    return template.render(interface=interface, name=name, uuid=uuid)
