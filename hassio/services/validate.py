"""Validate services schema."""
import voluptuous as vol

from ..utils.validate import schema_or
from .const import SERVICE_MQTT
from .modules.mqtt import SCHEMA_CONFIG_MQTT


SCHEMA_SERVICES_CONFIG = vol.Schema(
    {vol.Optional(SERVICE_MQTT, default=dict): schema_or(SCHEMA_CONFIG_MQTT)},
    extra=vol.REMOVE_EXTRA,
)
