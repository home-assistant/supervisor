"""Provide the MySQL Service."""

import logging
from typing import Any

import voluptuous as vol

from ...addons.addon import App
from ...exceptions import ServiceAlreadyProvidedError, ServiceNotProvidedError
from ...validate import network_port
from ..const import (
    ATTR_APP,
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

SCHEMA_CONFIG_MYSQL = SCHEMA_SERVICE_MYSQL.extend({vol.Required(ATTR_APP): str})


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
        """Return list of app slug they have enable that."""
        if not self.enabled:
            return []
        return [self._data[ATTR_APP]]

    async def set_service_data(self, app: App, data: dict[str, Any]) -> None:
        """Write the data into service object."""
        if self.enabled:
            raise ServiceAlreadyProvidedError(
                _LOGGER.debug,
                service=SERVICE_MYSQL,
                app=self._data[ATTR_APP],
            )

        self._data.update(data)
        self._data[ATTR_APP] = app.slug

        _LOGGER.info("Set %s as service provider for MySQL", app.slug)
        await self.save()

    async def del_service_data(self, app: App) -> None:
        """Remove the data from service object."""
        if not self.enabled:
            raise ServiceNotProvidedError(_LOGGER.debug, service=SERVICE_MYSQL)

        self._data.clear()
        await self.save()
