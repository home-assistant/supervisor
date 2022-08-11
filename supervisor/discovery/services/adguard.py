"""Discovery service for AdGuard."""
import voluptuous as vol

from ...validate import network_port
from ..const import ATTR_HOST, ATTR_PORT

SCHEMA = vol.Schema(
    {vol.Required(ATTR_HOST): str, vol.Required(ATTR_PORT): network_port}
)
