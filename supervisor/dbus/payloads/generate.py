"""Payload generators for DBUS communication."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

from ...host.const import AuthMethod

if TYPE_CHECKING:
    from ...host.network import Interface


INTERFACE_UPDATE_TEMPLATE: Path = (
    Path(__file__).parents[2].joinpath("dbus/payloads/interface_update.tmpl")
)


def interface_update_payload(interface: Interface) -> str:
    """Generate a payload for network interface update."""
    template = jinja2.Template(INTERFACE_UPDATE_TEMPLATE.read_text())
    wifi = {}

    if interface.wifi:
        if interface.wifi.mode == AuthMethod.WEB:
            wifi["auth-alg"] = "none"
            wifi["key-mgmt"] = "none"
        if interface.wifi.mode == AuthMethod.WPA_PSK:
            wifi["auth-alg"] = "shared"
            wifi["key-mgmt"] = "wpa-psk"

        wifi["ssid"] = ", ".join(
            [f"0x{x}" for x in interface.wifi.ssid.encode().hex(",").split(",")]
        )

    return template.render(interface=interface, wifi=wifi)
