"""Validate functions."""
import voluptuous as vol

NETWORK_PORT = vol.All(vol.Coerce(int), vol.Range(min=1, max=65535))
HOMEASSISTANT_DEVICES = [vol.Match(r"^[^/]*$")]


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
        return Schema([NETWORK_PORT])(data)

    # ip port mapping
    if isinstance(data, list) and len(data) == 2:
        return (vol.Coerce(str)(data[0]), NETWORK_PORT(data[1])


DOCKER_PORTS = vol.Schema({
    vol.All(vol.Coerce(str), vol.Match(r"^\d+(?:/tcp|/udp)?$")):
        convert_to_docker_ports,
})
