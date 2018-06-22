"""Init file for Hass.io hassos rest api."""
import asyncio
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import (
    ATTR_VERSION, ATTR_LAST_VERSION, ATTR_HOSTNAME, ATTR_FEATURES, ATTR_KERNEL,
    ATTR_TYPE, ATTR_OPERATING_SYSTEM, ATTR_CHASSIS, ATTR_DEPLOYMENT,
    ATTR_STATE, ATTR_NAME, ATTR_DESCRIPTON, ATTR_SERVICES)
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHassOS(CoreSysAttributes):
    """Handle rest api for hassos functions."""

    @api_process
    async def info(self, request):
        """Return hassos information."""
        return {
            ATTR_CHASSIS: self.sys_host.info.chassis,
            ATTR_VERSION: None,
            ATTR_LAST_VERSION: None,
            ATTR_TYPE: None,
            ATTR_FEATURES: self.sys_host.supperted_features,
            ATTR_HOSTNAME: self.sys_host.info.hostname,
            ATTR_OPERATING_SYSTEM: self.sys_host.info.operating_system,
            ATTR_DEPLOYMENT: self.sys_host.info.deployment,
            ATTR_KERNEL: self.sys_host.info.kernel,
        }

    @api_process
    def config(self, request):
        """Trigger config reload on HassOS."""
        return asyncio.shield(self.sys_hassos.config_reload())
