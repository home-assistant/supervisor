"""Interface for single service."""

from ..coresys import CoreSysAttributes


class ServiceInterface(CoreSysAttributes):
    """Interface class for service integration."""

    def __init__(self, coresys):
        """Initialize service interface."""
        self.coresys = coresys

    @property
    def _data(self):
        """Return data of this service."""
        return None

    @property
    def schema(self):
        """Return data schema of this service."""
        return None

    @property
    def provider(self):
        """Return name of service provider."""
        return None

    @property
    def enabled(self):
        """Return True if the service is in use."""
        return bool(self._data)

    def save(self):
        """Save changes."""
        self._services.data.save_data()

    async def get_service_data(self):
        """Return the requested service data."""
        if self.enabled:
            return self._data
        return None

    async def set_service_data(self, provider, data):
        """Write the data into service object."""
        raise NotImplementedError()
