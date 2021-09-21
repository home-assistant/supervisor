"""Provide the MQTT Service."""
import logging
from typing import Any

import voluptuous as vol

from supervisor.addons.addon import Addon
from supervisor.exceptions import ServicesError
from supervisor.validate import network_port

from ..const import (
    ATTR_ADDON,
    ATTR_HOST,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_PROTOCOL,
    ATTR_SSL,
    ATTR_USERNAME,
    SERVICE_MQTT,
)
from ..interface import ServiceInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_SERVICE_MQTT = vol.Schema(
    {
        vol.Required(ATTR_HOST): vol.Coerce(str),
        vol.Required(ATTR_PORT): network_port,
        vol.Optional(ATTR_USERNAME): vol.Coerce(str),
        vol.Optional(ATTR_PASSWORD): vol.Coerce(str),
        vol.Optional(ATTR_SSL, default=False): vol.Boolean(),
        vol.Optional(ATTR_PROTOCOL, default="3.1.1"): vol.All(
            vol.Coerce(str), vol.In(["3.1", "3.1.1"])
        ),
    }
)

SCHEMA_CONFIG_MQTT = SCHEMA_SERVICE_MQTT.extend(
    {vol.Required(ATTR_ADDON): vol.Coerce(str)}
)


class MQTTService(ServiceInterface):
    """Provide MQTT services."""

    @property
    def slug(self) -> str:
        """Return slug of this service."""
        return SERVICE_MQTT

    @property
    def _data(self) -> dict[str, Any]:
        """Return data of this service."""
        return self.sys_services.data.mqtt

    @property
    def schema(self) -> vol.Schema:
        """Return data schema of this service."""
        return SCHEMA_SERVICE_MQTT

    @property
    def active(self) -> list[str]:
        """Return list of addon slug they have enable that."""
        if not self.enabled:
            return []
        return [self._data[ATTR_ADDON]]

    def set_service_data(self, addon: Addon, data: dict[str, Any]) -> None:
        """Write the data into service object."""
        if self.enabled:
            _LOGGER.error(
                "There is already a MQTT service in use from %s", self._data[ATTR_ADDON]
            )
            raise ServicesError()

        self._data.update(data)
        self._data[ATTR_ADDON] = addon.slug

        _LOGGER.info("Set %s as service provider for mqtt", addon.slug)
        self.save()

    def del_service_data(self, addon: Addon) -> None:
        """Remove the data from service object."""
        if not self.enabled:
            _LOGGER.warning("Can't remove not exists services")
            raise ServicesError()

        self._data.clear()
        self.save()
