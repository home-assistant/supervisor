"""Init file for HassIO network rest api."""
import logging

from .utils import api_process, api_validate
from ..const import ATTR_AVAILABLE, ATTR_PROVIDER
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
        """Show network settings."""
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

        return await service.get_service_data("", body)

    @api_process
    def get_service(self, request):
        """Read data into a service."""
        service = self._extract_service(request)
        return service.get_service_data()
