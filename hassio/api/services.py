"""Init file for HassIO network rest api."""

from .utils import api_process, api_validate
from ..const import (
    ATTR_AVAILABLE, ATTR_PROVIDER, ATTR_SLUG, ATTR_SERVICES, REQUEST_FROM)
from ..coresys import CoreSysAttributes


class APIServices(CoreSysAttributes):
    """Handle rest api for services functions."""

    def _extract_service(self, request):
        """Return service, throw an exception if it doesn't exist."""
        service = self.sys_services.get(request.match_info.get('service'))
        if not service:
            raise RuntimeError("Service does not exist")

        return service

    @api_process
    async def list(self, request):
        """Show register services."""
        services = []
        for service in self.sys_services.list_services:
            services.append({
                ATTR_SLUG: service.slug,
                ATTR_AVAILABLE: service.enabled,
                ATTR_PROVIDER: service.provider,
            })

        return {ATTR_SERVICES: services}

    @api_process
    async def set_service(self, request):
        """Write data into a service."""
        service = self._extract_service(request)
        body = await api_validate(service.schema, request)

        return service.set_service_data(request[REQUEST_FROM], body)

    @api_process
    async def get_service(self, request):
        """Read data into a service."""
        service = self._extract_service(request)

        return {
            ATTR_AVAILABLE: service.enabled,
            service.slug: service.get_service_data(),
        }

    @api_process
    async def del_service(self, request):
        """Delete data into a service."""
        service = self._extract_service(request)
        return service.del_service_data(request[REQUEST_FROM])
