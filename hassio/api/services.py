"""Init file for HassIO network rest api."""
import logging

import voluptuous as vol

from .utils import api_process, api_validate
from ..const import ATTR_AVAILABLE, ATTR_PROVIDER
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class APIServices(CoreSysAttributes):
    """Handle rest api for services functions."""

    @api_process
    async def info(self, request):
        """Show network settings."""
        services = {}
        for service in self._services.list_services:
            services[service.slug] = {
                ATTR_AVAILABLE: service.enable,
                ATTR_PROVIDER: service.provider,
            }

        return services
