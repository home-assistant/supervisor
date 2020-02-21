"""Validate services schema."""
import voluptuous as vol

from ..utils.validate import schema_or
from .const import SERVICE_MQTT, SERVICE_MYSQL
from .modules.mqtt import SCHEMA_CONFIG_MQTT
from .modules.mysql import SCHEMA_CONFIG_MYSQL


SCHEMA_SERVICES_CONFIG = vol.Schema(
    {
        vol.Optional(SERVICE_MQTT, default=dict): schema_or(SCHEMA_CONFIG_MQTT),
        vol.Optional(SERVICE_MYSQL, default=dict): schema_or(SCHEMA_CONFIG_MYSQL),
    },
    extra=vol.REMOVE_EXTRA,
)
