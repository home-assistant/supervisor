"""Discovery service for MQTT."""
import voluptuous as vol

from supervisor.validate import network_port

from ..const import ATTR_HOST, ATTR_PORT, ATTR_API_KEY, ATTR_SERIAL


SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): vol.Coerce(str),
        vol.Required(ATTR_PORT): network_port,
        vol.Required(ATTR_SERIAL): vol.Coerce(str),
        vol.Required(ATTR_API_KEY): vol.Coerce(str),
    }
)
