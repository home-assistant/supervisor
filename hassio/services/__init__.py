"""Handle internal services discovery."""
import logging

from .mqtt import MQTTService
from .data import ServicesData
from ..coresys import CoreSysAttributes


AVAILABLE_SERVICES = {
    "mqtt": MQTTService
}


class ServiceManager(CoreSysAttributes):
    """Handle internal services discovery."""

    def __init__(self, coresys):
        """Initialize Services handler."""
        self.coresys = coresys
        self.data = ServicesData()
        self.services_obj = {}

    def get(self, slug):
        """Return service object from slug."""
        return self.services_obj.get(slug)

    async def load(self):
        """Load available services."""
        for slug, service in AVAILABLE_SERVICES.items():
            self.services_obj[slug] = service(self.coresys)
