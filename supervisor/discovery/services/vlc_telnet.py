"""Discovery service for VLC Telnet."""
import voluptuous as vol

from supervisor.validate import network_port

from ..const import ATTR_HOST, ATTR_PASSWORD, ATTR_PORT

# pylint: disable=no-value-for-parameter
SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): str,
        vol.Required(ATTR_PORT): network_port,
        vol.Required(ATTR_PASSWORD): str,
    }
)
