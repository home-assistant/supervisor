"""Payload generators for DBUS communication."""
from pathlib import Path

import jinja2

from ...const import ATTR_ADDRESS, ATTR_DNS, ATTR_METHOD, ATTR_PREFIX
from ..const import InterfaceMethod
from ..network.utils import ip2int

INTERFACE_UPDATE_TEMPLATE: Path = (
    Path(__file__).parents[2].joinpath("dbus/payloads/interface_update.tmpl")
)


def interface_update_payload(interface, **kwargs) -> str:
    """Generate a payload for network interface update."""
    template = jinja2.Template(INTERFACE_UPDATE_TEMPLATE.read_text())
    if kwargs.get(ATTR_DNS):
        kwargs[ATTR_DNS] = [ip2int(x.strip()) for x in kwargs[ATTR_DNS]]

    if kwargs.get(ATTR_METHOD):
        kwargs[ATTR_METHOD] = (
            InterfaceMethod.MANUAL
            if kwargs[ATTR_METHOD] == "static"
            else InterfaceMethod.AUTO
        )

    if kwargs.get(ATTR_ADDRESS):
        if "/" in kwargs[ATTR_ADDRESS]:
            kwargs[ATTR_PREFIX] = kwargs[ATTR_ADDRESS].split("/")[-1]
            kwargs[ATTR_ADDRESS] = kwargs[ATTR_ADDRESS].split("/")[0]
        kwargs[ATTR_METHOD] = InterfaceMethod.MANUAL

    return template.render(interface=interface, options=kwargs)
