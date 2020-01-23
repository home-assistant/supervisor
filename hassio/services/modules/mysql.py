"""Provide the MySQL Service."""
import logging
from typing import Any, Dict

from hassio.addons.addon import Addon
from hassio.exceptions import ServicesError
from hassio.validate import network_port
import voluptuous as vol

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
        vol.Required(ATTR_HOST): vol.Coerce(str),
        vol.Required(ATTR_PORT): network_port,
        vol.Optional(ATTR_USERNAME): vol.Coerce(str),
        vol.Optional(ATTR_PASSWORD): vol.Coerce(str),
    }
)

SCHEMA_CONFIG_MYSQL = SCHEMA_SERVICE_MYSQL.extend(
    {vol.Required(ATTR_ADDON): vol.Coerce(str)}
)


class MySQLService(ServiceInterface):
    """Provide MySQL services."""

    @property
    def slug(self) -> str:
        """Return slug of this service."""
        return SERVICE_MYSQL

    @property
    def _data(self) -> Dict[str, Any]:
        """Return data of this service."""
        return self.sys_services.data.mysql

    @property
    def schema(self) -> vol.Schema:
        """Return data schema of this service."""
        return SCHEMA_SERVICE_MYSQL

    def set_service_data(self, addon: Addon, data: Dict[str, Any]) -> None:
        """Write the data into service object."""
        if self.enabled:
            _LOGGER.error(
                "There is already a MySQL in use from %s", self._data[ATTR_ADDON]
            )
            raise ServicesError()

        self._data.update(data)
        self._data[ATTR_ADDON] = addon.slug

        _LOGGER.info("Set %s as service provider for MySQL", addon.slug)
        self.save()

    def del_service_data(self, addon: Addon) -> None:
        """Remove the data from service object."""
        if not self.enabled:
            _LOGGER.warning("Can't remove not exists services")
            raise ServicesError()

        self._data.clear()
        self.save()
