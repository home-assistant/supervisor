"""Discovery service for motionEye."""
import voluptuous as vol

from ..const import ATTR_URL

SCHEMA = vol.Schema({vol.Required(ATTR_URL): vol.Coerce(str)})
