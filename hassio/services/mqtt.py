"""Provide the MQTT Service."""
import logging

from .interface import ServiceInterface
from .validate import SCHEMA_SERVICE_MQTT
from ..const import ATTR_ADDON, SERVICE_MQTT
from ..exceptions import ServicesError

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

    def set_service_data(self, addon, data):
        """Write the data into service object."""
        if self.enabled:
            _LOGGER.error("It is already a MQTT in use from %s", self.provider)
            raise ServicesError()

        self._data.update(data)
        self._data[ATTR_ADDON] = addon.slug
        self.save()

    def del_service_data(self, addon):
        """Remove the data from service object."""
        if not self.enabled:
            _LOGGER.warning("Can't remove not exists services")
            raise ServicesError()

        self._data.clear()
        self.save()
