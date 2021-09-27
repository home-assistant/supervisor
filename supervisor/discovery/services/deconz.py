"""Discovery service for MQTT."""
import voluptuous as vol

from supervisor.validate import network_port

from ..const import ATTR_API_KEY, ATTR_HOST, ATTR_PORT, ATTR_SERIAL

SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): str,
        vol.Required(ATTR_PORT): network_port,
        vol.Required(ATTR_SERIAL): str,
        vol.Required(ATTR_API_KEY): str,
    }
)
