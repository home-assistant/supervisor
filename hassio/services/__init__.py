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

    async def load(self):
        """Load available services."""
