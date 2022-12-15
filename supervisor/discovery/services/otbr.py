"""Discovery service for OpenThread Border Router."""
import voluptuous as vol

from ...validate import network_port
from ..const import ATTR_HOST, ATTR_REST_PORT

# pylint: disable=no-value-for-parameter
SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_HOST): str,
        vol.Required(ATTR_REST_PORT): network_port,
    }
)
