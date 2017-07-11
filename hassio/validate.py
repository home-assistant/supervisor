"""Validate functions."""
import voluptuous as vol

from .const import ATTR_DEVICES, ATTR_IMAGE


NETWORK_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
HASS_DEVICES = [vol.Match(r"^[^/]*$")]


def convert_to_docker_ports(data):
    """Convert data into docker port list."""
    # dynamic ports
    if data is None:
        return

    # single port
    if isinstance(data, int):
        return NETWORK_PORT(data)

    # port list
    if isinstance(data, list) and len(data) > 2:
        return vol.Schema([NETWORK_PORT])(data)

    # ip port mapping
    if isinstance(data, list) and len(data) == 2:
        return (vol.Coerce(str)(data[0]), NETWORK_PORT(data[1]))

    raise vol.Invalid("Can't validate docker host settings")


DOCKER_PORTS = vol.Schema({
    vol.All(vol.Coerce(str), vol.Match(r"^\d+(?:/tcp|/udp)?$")):
        convert_to_docker_ports,
})


SCHEMA_HASS_CONFIG = vol.Schema({
    vol.Optional(ATTR_DEVICES, default=[]): HASS_DEVICES,
    vol.Optional(ATTR_IMAGE): vol.Coerce(str)
})
