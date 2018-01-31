"""Interface for single service."""

from ..coresys import CoreSysAttributes

class ServiceInterface(CoreSysAttributes):
    """Interface class for service integration."""

    def __init__(self, coresys):
        """Initialize service interface."""
        self.coresys = coresys

    @property
    def schema(self):
        """Return data schema of this service."""
        return None

    async def get_service_data(self):
        """Return the requested service data."""
        raise NotImplementedError()

    async def set_service_data(self, data):
        """Write the data into service object."""
        raise NotImplementedError()
