"""Provide the MQTT Service."""
import logging

from .interface import ServiceInterface
from .validate import SCHEMA_SERVICE_MQTT
from ..const import (
    ATTR_PROVIDER, SERVICE_MQTT, ATTR_HOST, ATTR_PORT, ATTR_USERNAME,
    ATTR_PASSWORD, ATTR_PROTOCOL, ATTR_DISCOVERY_ID)

_LOGGER = logging.getLogger(__name__)


class MQTTService(ServiceInterface):
    """Provide MQTT services."""

    @property
    def slug(self):
        """Return slug of this service."""
        return SERVICE_MQTT

    @property
    def _data(self):
        """Return data of this service."""
        return self.sys_services.data.mqtt

    @property
    def schema(self):
        """Return data schema of this service."""
        return SCHEMA_SERVICE_MQTT

    @property
    def provider(self):
        """Return name of service provider."""
        return self._data.get(ATTR_PROVIDER)

    @property
    def hass_config(self):
        """Return Home Assistant MQTT config."""
        if not self.enabled:
            return None

        hass_config = {
            'host': self._data[ATTR_HOST],
            'port': self._data[ATTR_PORT],
            'protocol': self._data[ATTR_PROTOCOL]
        }
        if ATTR_USERNAME in self._data:
            hass_config['user']: self._data[ATTR_USERNAME]
        if ATTR_PASSWORD in self._data:
            hass_config['password']: self._data[ATTR_PASSWORD]

        return hass_config

    def set_service_data(self, provider, data):
        """Write the data into service object."""
        if self.enabled:
            _LOGGER.error("It is already a MQTT in use from %s", self.provider)
            return False

        self._data.update(data)
        self._data[ATTR_PROVIDER] = provider

        if provider == 'homeassistant':
            _LOGGER.info("Use MQTT settings from Home Assistant")
            self.save()
            return True

        # Discover MQTT to Home Assistant
        message = self.sys_discovery.send(
            provider, SERVICE_MQTT, None, self.hass_config)

        self._data[ATTR_DISCOVERY_ID] = message.uuid
        self.save()
        return True

    def del_service_data(self, provider):
        """Remove the data from service object."""
        if not self.enabled:
            _LOGGER.warning("Can't remove not exists services")
            return False

        discovery_id = self._data.get(ATTR_DISCOVERY_ID)
        if discovery_id:
            self.sys_discovery.remove(
                self.sys_discovery.get(discovery_id))

        self._data.clear()
        self.save()
        return True
