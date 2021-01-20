"""Discovery service for OpenZwave MQTT."""
import voluptuous as vol

from supervisor.validate import network_port

from ..const import ATTR_HOST, ATTR_PASSWORD, ATTR_PORT, ATTR_USERNAME

# pylint: disable=no-value-for-parameter
SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): str,
        vol.Required(ATTR_PORT): network_port,
        vol.Required(ATTR_USERNAME): vol.Coerce(str),
        vol.Required(ATTR_PASSWORD): vol.Coerce(str),
    }
)
