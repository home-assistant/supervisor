"""Provide MQTT Service."""

from .interface import ServiceInterface
from .validate import SCHEMA_SERVICE_MQTT


class MQTTService(ServiceInterface):
    """Provide mqtt services."""

    @property
    def _data(self):
        """Return data of this service."""
        return self._services.data.mqtt

    @property
    def schema(self):
        """Return data schema of this service."""
        return SCHEMA_SERVICE_MQTT
