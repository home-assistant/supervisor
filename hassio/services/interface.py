"""Interface for single service."""
from typing import Any, Dict, List, Optional

import voluptuous as vol

from ..addons.addon import Addon
from ..const import PROVIDE_SERVICE
from ..coresys import CoreSys, CoreSysAttributes


class ServiceInterface(CoreSysAttributes):
    """Interface class for service integration."""

    def __init__(self, coresys: CoreSys):
        """Initialize service interface."""
        self.coresys: CoreSys = coresys

    @property
    def slug(self) -> str:
        """Return slug of this service."""
        raise NotImplementedError()

    @property
    def _data(self) -> Dict[str, Any]:
        """Return data of this service."""
        raise NotImplementedError()

    @property
    def schema(self) -> vol.Schema:
        """Return data schema of this service."""
        raise NotImplementedError()

    @property
    def providers(self) -> List[str]:
        """Return name of service providers addon."""
        addons = []
        for addon in self.sys_addons.installed:
            if addon.services_role.get(self.slug) == PROVIDE_SERVICE:
                addons.append(addon.slug)
        return addons

    @property
    def enabled(self) -> bool:
        """Return True if the service is in use."""
        return bool(self._data)

    def save(self) -> None:
        """Save changes."""
        self.sys_services.data.save_data()

    def get_service_data(self) -> Optional[Dict[str, Any]]:
        """Return the requested service data."""
        if self.enabled:
            return self._data
        return None

    def set_service_data(self, addon: Addon, data: Dict[str, Any]) -> None:
        """Write the data into service object."""
        raise NotImplementedError()

    def del_service_data(self, addon: Addon) -> None:
        """Remove the data from service object."""
        raise NotImplementedError()
