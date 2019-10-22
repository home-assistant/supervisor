"""Discovery service for Almond."""
import voluptuous as vol

from hassio.validate import NETWORK_PORT

from ..const import ATTR_HOST, ATTR_PORT


SCHEMA = vol.Schema(
    {vol.Required(ATTR_HOST): vol.Coerce(str), vol.Required(ATTR_PORT): NETWORK_PORT}
)
