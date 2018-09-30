"""Validate services schema."""
import voluptuous as vol

from ..const import (
    SERVICE_MQTT, ATTR_HOST, ATTR_PORT, ATTR_PASSWORD, ATTR_USERNAME, ATTR_SSL,
    ATTR_ADDON, ATTR_PROTOCOL)
from ..validate import NETWORK_PORT
from ..utils.validate import schema_or


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


SCHEMA_SERVICES_CONFIG = vol.Schema({
    vol.Optional(SERVICE_MQTT, default=dict): schema_or(SCHEMA_CONFIG_MQTT),
}, extra=vol.REMOVE_EXTRA)


DISCOVERY_SERVICES = {
    SERVICE_MQTT: SCHEMA_SERVICE_MQTT,
}
