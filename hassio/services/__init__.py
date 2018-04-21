"""Handle internal services discovery."""

from .mqtt import MQTTService
from .data import ServicesData
from ..const import SERVICE_MQTT
from ..coresys import CoreSysAttributes


AVAILABLE_SERVICES = {
    SERVICE_MQTT: MQTTService
}


class ServiceManager(CoreSysAttributes):
    """Handle internal services discovery."""

    def __init__(self, coresys):
        """Initialize Services handler."""
        self.coresys = coresys
        self.data = ServicesData()
        self.services_obj = {}

    @property
    def list_services(self):
        """Return a list of services."""
        return list(self.services_obj.values())

    def get(self, slug):
        """Return service object from slug."""
        return self.services_obj.get(slug)

    async def load(self):
        """Load available services."""
        for slug, service in AVAILABLE_SERVICES.items():
            self.services_obj[slug] = service(self.coresys)

        # Read exists discovery messages
        self.sys_discovery.load()

    def reset(self):
        """Reset available data."""
        self.data.reset_data()
        self.sys_discovery.load()
