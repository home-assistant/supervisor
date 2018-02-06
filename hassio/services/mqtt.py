"""Provide MQTT Service."""
import logging

from .interface import ServiceInterface
from .validate import SCHEMA_SERVICE_MQTT
from ..const import (
    ATTR_PROVIDER, SERVICE_MQTT, ATTR_HOST, ATTR_PORT, ATTR_USERNAME,
    ATTR_PASSWORD, ATTR_PROTOCOL)

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
            _LOGGER.info("Use mqtt settings from Home-Assistant")
            return True

        # discover mqtt to homeassistant
        hass_config = {
            'host': data[ATTR_HOST],
            'port': data[ATTR_PORT],
            'protocol': data[ATTR_PROTOCOL]
        }
        if ATTR_USERNAME in data:
            hass_config['user']: data[ATTR_USERNAME]
        if ATTR_PASSWORD in data:
            hass_config['password']: data[ATTR_PASSWORD]

        await self._services.discovery.send(
            provider, SERVICE_MQTT, None, hass_config)
        return True

    async def del_service_data(self, provider):
        """Remove the data from service object."""
        raise NotImplementedError()
