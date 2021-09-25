"""Init file for Supervisor Home Assistant RESTful API."""
import logging
from typing import Any

from aiohttp import web
import voluptuous as vol

from ..const import (
    ATTR_HOSTNAME,
    ATTR_LOGGING,
    ATTR_PASSWORD,
    ATTR_REGISTRIES,
    ATTR_STORAGE,
    ATTR_USERNAME,
    ATTR_VERSION,
)
from ..coresys import CoreSysAttributes
from .utils import api_process, api_validate

_LOGGER: logging.Logger = logging.getLogger(__name__)

SCHEMA_DOCKER_REGISTRY = vol.Schema(
    {
        str: {
            vol.Required(ATTR_USERNAME): str,
            vol.Required(ATTR_PASSWORD): str,
        }
    }
)


class APIDocker(CoreSysAttributes):
    """Handle RESTful API for Docker configuration."""

    @api_process
    async def registries(self, request) -> dict[str, Any]:
        """Return the list of registries."""
        data_registries = {}
        for hostname, registry in self.sys_docker.config.registries.items():
            data_registries[hostname] = {
                ATTR_USERNAME: registry[ATTR_USERNAME],
            }

        return {ATTR_REGISTRIES: data_registries}

    @api_process
    async def create_registry(self, request: web.Request):
        """Create a new docker registry."""
        body = await api_validate(SCHEMA_DOCKER_REGISTRY, request)

        for hostname, registry in body.items():
            self.sys_docker.config.registries[hostname] = registry

        self.sys_docker.config.save_data()

    @api_process
    async def remove_registry(self, request: web.Request):
        """Delete a docker registry."""
        hostname = request.match_info.get(ATTR_HOSTNAME)
        del self.sys_docker.config.registries[hostname]
        self.sys_docker.config.save_data()

    @api_process
    async def info(self, request: web.Request):
        """Get docker info."""
        data_registries = {}
        for hostname, registry in self.sys_docker.config.registries.items():
            data_registries[hostname] = {
                ATTR_USERNAME: registry[ATTR_USERNAME],
            }
        return {
            ATTR_VERSION: self.sys_docker.info.version,
            ATTR_STORAGE: self.sys_docker.info.storage,
            ATTR_LOGGING: self.sys_docker.info.logging,
            ATTR_REGISTRIES: data_registries,
        }
