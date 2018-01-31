"""Validate services schema."""

import voluptuous as vol

from ..const import (
    ATTR_MQTT, ATTR_HOST, ATTR_PORT, ATTR_PASSWORD, ATTR_USERNAME, ATTR_SSL,
    ATTR_PROVIDER, ATTR_PROTOCOL)
from ..validate import NETWORK_PORT


SCHEMA_SERVICE = vol.Schema({
    vol.Optional(ATTR_PROVIDER): vol.Coerce(str),
})


# pylint: disable=no-value-for-parameter
SCHEMA_SERVICE_MQTT = SCHEMA_SERVICE.extend({
    vol.Optional(ATTR_HOST): vol.Coerce(str),
    vol.Optional(ATTR_PORT): NETWORK_PORT,
    vol.Optional(ATTR_USERNAME): vol.Coerce(str),
    vol.Optional(ATTR_PASSWORD): vol.Coerce(str),
    vol.Optional(ATTR_SSL): vol.Boolean(),
    vol.Optional(ATTR_PROTOCOL):
        vol.All(vol.Coerce(str), vol.In(['3.1', '3.1.1'])),
}, extra=vol.REMOVE_EXTRA)


SCHEMA_SERVICES_FILE = vol.Schema({
    vol.Optional(ATTR_MQTT, default=dict): SCHEMA_SERVICE_MQTT,
}, extra=vol.REMOVE_EXTRA)
