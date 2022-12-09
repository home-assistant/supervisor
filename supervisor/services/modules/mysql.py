"""Provide the MySQL Service."""
import logging
from typing import Any

import voluptuous as vol

from ...addons.addon import Addon
from ...exceptions import ServicesError
from ...validate import network_port
from ..const import (
    ATTR_ADDON,
    ATTR_HOST,
    ATTR_PASSWORD,
    ATTR_PORT,
    ATTR_USERNAME,
    SERVICE_MYSQL,
)
from ..interface import ServiceInterface

_LOGGER: logging.Logger = logging.getLogger(__name__)


# pylint: disable=no-value-for-parameter
SCHEMA_SERVICE_MYSQL = vol.Schema(
    {
        vol.Required(ATTR_HOST): str,
        vol.Required(ATTR_PORT): network_port,
        vol.Optional(ATTR_USERNAME): str,
        vol.Optional(ATTR_PASSWORD): str,
    }
)

SCHEMA_CONFIG_MYSQL = SCHEMA_SERVICE_MYSQL.extend({vol.Required(ATTR_ADDON): str})


class MySQLService(ServiceInterface):
    """Provide MySQL services."""

    @property
    def slug(self) -> str:
        """Return slug of this service."""
        return SERVICE_MYSQL

    @property
    def _data(self) -> dict[str, Any]:
        """Return data of this service."""
        return self.sys_services.data.mysql

    @property
    def schema(self) -> vol.Schema:
        """Return data schema of this service."""
        return SCHEMA_SERVICE_MYSQL

    @property
    def active(self) -> list[str]:
        """Return list of addon slug they have enable that."""
        if not self.enabled:
            return []
        return [self._data[ATTR_ADDON]]

    def set_service_data(self, addon: Addon, data: dict[str, Any]) -> None:
        """Write the data into service object."""
        if self.enabled:
            raise ServicesError(
                f"There is already a MySQL service in use from {self._data[ATTR_ADDON]}",
                _LOGGER.error,
            )

        self._data.update(data)
        self._data[ATTR_ADDON] = addon.slug

        _LOGGER.info("Set %s as service provider for MySQL", addon.slug)
        self.save()

    def del_service_data(self, addon: Addon) -> None:
        """Remove the data from service object."""
        if not self.enabled:
            raise ServicesError("Can't remove not exists services", _LOGGER.warning)

        self._data.clear()
        self.save()
