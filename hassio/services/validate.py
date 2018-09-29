"""Validate services schema."""
import re

import voluptuous as vol

from ..const import (
    SERVICE_MQTT, ATTR_HOST, ATTR_PORT, ATTR_PASSWORD, ATTR_USERNAME, ATTR_SSL,
    ATTR_ADDON, ATTR_PROTOCOL, ATTR_DISCOVERY, ATTR_COMPONENT, ATTR_UUID,
    ATTR_PLATFORM, ATTR_CONFIG, ATTR_SERVICE)
from ..validate import NETWORK_PORT

UUID_MATCH = re.compile(r"^[0-9a-f]{32}$")

SERVICE_ALL = [
    SERVICE_MQTT
]


def schema_or(schema):
    """Allow schema or empty."""
    def _wrapper(value):
        """Wrapper for validator."""
        if not value:
            return value
        return schema(value)

    return _wrapper


SCHEMA_DISCOVERY = vol.Schema([
    vol.Schema({
        vol.Required(ATTR_UUID): vol.Match(UUID_MATCH),
        vol.Required(ATTR_ADDON): vol.Coerce(str),
        vol.Required(ATTR_SERVICE): vol.In(SERVICE_ALL),
        vol.Required(ATTR_COMPONENT): vol.Coerce(str),
        vol.Required(ATTR_PLATFORM): vol.Maybe(vol.Coerce(str)),
        vol.Required(ATTR_CONFIG): vol.Maybe(dict),
    }, extra=vol.REMOVE_EXTRA)
])


# pylint: disable=no-value-for-parameter
SCHEMA_SERVICE_MQTT = vol.Schema({
    vol.Required(ATTR_HOST): vol.Coerce(str),
    vol.Required(ATTR_PORT): NETWORK_PORT,
    vol.Optional(ATTR_USERNAME): vol.Coerce(str),
    vol.Optional(ATTR_PASSWORD): vol.Coerce(str),
    vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
    vol.Optional(ATTR_PROTOCOL, default='3.1.1'):
        vol.All(vol.Coerce(str), vol.In(['3.1', '3.1.1'])),
})


SCHEMA_CONFIG_MQTT = SCHEMA_SERVICE_MQTT.extend({
    vol.Required(ATTR_ADDON): vol.Coerce(str),
})


SCHEMA_SERVICES_FILE = vol.Schema({
    vol.Optional(SERVICE_MQTT, default=dict): schema_or(SCHEMA_CONFIG_MQTT),
    vol.Optional(ATTR_DISCOVERY, default=list): schema_or(SCHEMA_DISCOVERY),
}, extra=vol.REMOVE_EXTRA)


DISCOVERY_SERVICES = {
    SERVICE_MQTT: SCHEMA_SERVICE_MQTT,
}
