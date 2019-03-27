"""Validate services schema."""
import voluptuous as vol

from ..const import ATTR_ADDON, ATTR_CONFIG, ATTR_DISCOVERY, ATTR_SERVICE, ATTR_UUID
from ..services.validate import SCHEMA_SERVICE_MQTT
from ..utils.validate import schema_or
from ..validate import UUID_MATCH
from .const import DISCOVERY_DECONZ, DISCOVERY_MQTT

DISCOVERY_ALL = vol.In([DISCOVERY_MQTT, DISCOVERY_DECONZ])

SCHEMA_DISCOVERY = vol.Schema(
    [
        vol.Schema(
            {
                vol.Required(ATTR_UUID): UUID_MATCH,
                vol.Required(ATTR_ADDON): vol.Coerce(str),
                vol.Required(ATTR_SERVICE): DISCOVERY_ALL,
                vol.Required(ATTR_CONFIG): vol.Maybe(dict),
            },
            extra=vol.REMOVE_EXTRA,
        )
    ]
)

SCHEMA_DISCOVERY_CONFIG = vol.Schema(
    {vol.Optional(ATTR_DISCOVERY, default=list): schema_or(SCHEMA_DISCOVERY)},
    extra=vol.REMOVE_EXTRA,
)


DISCOVERY_SERVICES = {DISCOVERY_MQTT: SCHEMA_SERVICE_MQTT}
