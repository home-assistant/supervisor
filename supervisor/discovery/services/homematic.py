"""Discovery service for HomeMatic."""
import voluptuous as vol

from supervisor.validate import network_port

from ..const import ATTR_HOST, ATTR_PORT

SCHEMA = vol.Schema(
    {
        vol.Coerce(str): vol.Schema(
            {
                vol.Required(ATTR_HOST): vol.Coerce(str),
                vol.Required(ATTR_PORT): network_port,
            }
        )
    }
)
