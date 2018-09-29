"""Interface for single service."""

from ..coresys import CoreSysAttributes


class ServiceInterface(CoreSysAttributes):
    """Interface class for service integration."""

    def __init__(self, coresys):
        """Initialize service interface."""
        self.coresys = coresys

    @property
    def slug(self):
        """Return slug of this service."""
        return None

    @property
    def _data(self):
        """Return data of this service."""
        return None

    @property
    def schema(self):
        """Return data schema of this service."""
        return None

    @property
    def providers(self):
        """Return name of service providers addon."""
        addons = []
        for addon in self.sys_addons.list_installed:
            if addon.services_role.get(self.slug) == 'rw':
                addons.append(addon.slug)
        return addons

    @property
    def enabled(self):
        """Return True if the service is in use."""
        return bool(self._data)

    def save(self):
        """Save changes."""
        self.sys_services.data.save_data()

    def get_service_data(self):
        """Return the requested service data."""
        if self.enabled:
            return self._data
        return None

    def set_service_data(self, addon, data):
        """Write the data into service object."""
        raise NotImplementedError()

    def del_service_data(self, addon):
        """Remove the data from service object."""
        raise NotImplementedError()
