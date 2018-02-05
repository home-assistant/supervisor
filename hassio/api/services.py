"""Init file for HassIO network rest api."""
import asyncio
import logging

from .utils import api_process, api_validate
from ..const import ATTR_AVAILABLE, ATTR_PROVIDER, REQUEST_FROM
from ..coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class APIServices(CoreSysAttributes):
    """Handle rest api for services functions."""

    def _extract_service(self, request):
        """Return service and if not exists trow a exception."""
        service = self._services.get(request.match_info.get('service'))
        if not service:
            raise RuntimeError("Service not exists")

        return service

    @api_process
    async def list(self, request):
        """Show register services."""
        services = {}
        for service in self._services.list_services:
            services[service.slug] = {
                ATTR_AVAILABLE: service.enable,
                ATTR_PROVIDER: service.provider,
            }

        return services

    @api_process
    async def set_service(self, request):
        """Write data into a service."""
        service = self._extract_service(request)
        body = await api_validate(service.schema, request)

        return await asyncio.shield(
            service.set_service_data(request[REQUEST_FROM], body),
            loop=self._loop)

    @api_process
    def get_service(self, request):
        """Read data into a service."""
        service = self._extract_service(request)
        return service.get_service_data()
