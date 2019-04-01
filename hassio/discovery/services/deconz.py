"""Discovery service for MQTT."""
import voluptuous as vol

from hassio.validate import NETWORK_PORT

from ..const import ATTR_HOST, ATTR_PORT, ATTR_API_KEY, ATTR_SERIAL


SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): vol.Coerce(str),
        vol.Required(ATTR_PORT): NETWORK_PORT,
        vol.Required(ATTR_SERIAL): vol.Coerce(str),
        vol.Required(ATTR_API_KEY): vol.Coerce(str),
    }
)
