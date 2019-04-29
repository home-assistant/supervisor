"""Init file for Hass.io add-on data."""
import logging

from ..const import (
    ATTR_SYSTEM,
    ATTR_USER,
    FILE_HASSIO_ADDONS,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..utils.json import JsonConfig
from .validate import SCHEMA_ADDONS_FILE

_LOGGER = logging.getLogger(__name__)


class AddonsData(JsonConfig, CoreSysAttributes):
    """Hold data for installed Add-ons inside Hass.io."""

    def __init__(self, coresys: CoreSys):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_ADDONS, SCHEMA_ADDONS_FILE)
        self.coresys: CoreSys = coresys

    @property
    def user(self):
        """Return local add-on user data."""
        return self._data[ATTR_USER]

    @property
    def system(self):
        """Return local add-on data."""
        return self._data[ATTR_SYSTEM]

    def _set_install(self, image: str, version: str) -> None:
        """Set addon as installed."""
        self._data.system[self._id] = deepcopy(self._data.cache[self._id])
        self._data.user[self._id] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: version,
            ATTR_IMAGE: image,
        }
        self.save_data()

    def uninstall(self, addon) -> None:
        """Set add-on as uninstalled."""
        self._data.system.pop(addon.slug, None)
        self._data.user.pop(addon.slug, None)
        self.save_data()

    def set_update(self, image: str, version: str) -> None:
        """Update version of add-on."""
        self._data.system[self._id] = deepcopy(self._data.cache[self._id])
        self._data.user[self._id].update({
            ATTR_VERSION: version,
            ATTR_IMAGE: image,
        })
        self.save_data()

    def restore_data(self, user: Dict[str, Any], system: Dict[str, Any], image: str) -> None:
        """Restore data to add-on."""
        self._data.user[self._id] = deepcopy(user)
        self._data.system[self._id] = deepcopy(system)

        self._data.user[self._id][ATTR_IMAGE] = image
        self.save_data()