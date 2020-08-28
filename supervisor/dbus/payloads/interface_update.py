"""Payload generators for DBUS communication."""
from ...const import ATTR_ADDRESS, ATTR_DNS, ATTR_GATEWAY, ATTR_METHOD, ATTR_PREFIX
from ..const import InterfaceMethod
from ..network.utils import ip2int


def interface_update_payload(interface, **kwargs) -> str:
    """Generate a payload for network interface update."""
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

    if kwargs.get(ATTR_METHOD) == "auto":
        return f"""{{
                    'connection':
                        {{
                            'id': <'{interface.id}'>,
                            'type': <'{interface.type}'>
                        }},
                    'ipv4':
                        {{
                            'method': <'{InterfaceMethod.AUTO}'>
                        }}
                }}"""

    return f"""{{
                    'connection':
                        {{
                            'id': <'{interface.id}'>,
                            'type': <'{interface.type}'>
                        }},
                    'ipv4':
                        {{
                            'method': <'{InterfaceMethod.MANUAL}'>,
                            'dns': <[{",".join([f"uint32 {x}" for x in kwargs.get(ATTR_DNS, interface.nameservers)])}]>,
                            'address-data': <[
                                {{
                                    'address': <'{kwargs.get(ATTR_ADDRESS, interface.ip_address)}'>,
                                    'prefix': <uint32 {kwargs.get(ATTR_PREFIX, interface.prefix)}>
                                }}]>,
                            'gateway': <'{kwargs.get(ATTR_GATEWAY, interface.gateway)}'>
                                }}
                }}"""
