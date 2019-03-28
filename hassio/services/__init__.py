"""Handle internal services discovery."""
from typing import Dict, List

from ..coresys import CoreSys, CoreSysAttributes
from .const import SERVICE_MQTT
from .data import ServicesData
from .interface import ServiceInterface
from .modules.mqtt import MQTTService

AVAILABLE_SERVICES = {SERVICE_MQTT: MQTTService}


class ServiceManager(CoreSysAttributes):
    """Handle internal services discovery."""

    def __init__(self, coresys: CoreSys):
        """Initialize Services handler."""
        self.coresys: CoreSys = coresys
        self.data: ServicesData = ServicesData()
        self.services_obj: Dict[str, ServiceInterface] = {}

    @property
    def list_services(self) -> List[ServiceInterface]:
        """Return a list of services."""
        return list(self.services_obj.values())

    def get(self, slug: str) -> ServiceInterface:
        """Return service object from slug."""
        return self.services_obj.get(slug)

    async def load(self) -> None:
        """Load available services."""
        for slug, service in AVAILABLE_SERVICES.items():
            self.services_obj[slug] = service(self.coresys)

    def reset(self) -> None:
        """Reset available data."""
        self.data.reset_data()
