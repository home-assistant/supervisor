"""Provide MQTT Service."""
import logging

from .interface import ServiceInterface
from .validate import SCHEMA_SERVICE_MQTT
from ..const import ATTR_PROVIDER, SERVICE_MQTT

_LOGGER = logging.getLogger(__name__)


class MQTTService(ServiceInterface):
    """Provide mqtt services."""

    @property
    def slug(self):
        """Return slug of this service."""
        return SERVICE_MQTT

    @property
    def _data(self):
        """Return data of this service."""
        return self._services.data.mqtt

    @property
    def schema(self):
        """Return data schema of this service."""
        return SCHEMA_SERVICE_MQTT

    @property
    def provider(self):
        """Return name of service provider."""
        return self._data.get(ATTR_PROVIDER)

    async def set_service_data(self, provider, data):
        """Write the data into service object."""
        if self.enabled:
            _LOGGER.error("It is already a mqtt in use from %s", self.provider)
            return False

        self._data = data
        self._data[ATTR_PROVIDER] = provider
        self.save()

        if provider == 'homeassistant':
            return

        # discover mqtt to homeassistant
        # fixme
