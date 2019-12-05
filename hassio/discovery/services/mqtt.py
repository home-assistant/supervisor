"""Discovery service for MQTT."""
import voluptuous as vol

from hassio.validate import network_port

from ..const import (
    ATTR_HOST,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_PROTOCOL,
    ATTR_SSL,
    ATTR_USERNAME,
)

# pylint: disable=no-value-for-parameter
SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): vol.Coerce(str),
        vol.Required(ATTR_PORT): network_port,
        vol.Optional(ATTR_USERNAME): vol.Coerce(str),
        vol.Optional(ATTR_PASSWORD): vol.Coerce(str),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_PROTOCOL, default="3.1.1"): vol.All(
            vol.Coerce(str), vol.In(["3.1", "3.1.1"])
        ),
    }
)
