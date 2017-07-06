"""Validate functions."""
import voluptuous as vol

network_port = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
hass_devices = [vol.Match(r"^[^/]*$")]


def convert_to_docker_ports(data):
    """Convert data into docker port list."""
    # dynamic ports
    if data is None:
        return

    # single port
    if isinstance(data, int):
        return network_port(data)

    # port list
    if isinstance(data, list) and len(data) > 2:
        return Schema([network_port])(data)

    # ip port mapping
    if isinstance(data, list) and len(data) == 2:
        return (vol.Coerce(str)(data[0]), network_port(data[1]))

    raise vol.Invalid("Can't validate docker host settings")


docker_ports = vol.Schema({
    vol.All(vol.Coerce(str), vol.Match(r"^\d+(?:/tcp|/udp)?$")):
        convert_to_docker_ports,
})
