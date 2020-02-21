"""Init file for Supervisor add-on data."""
from copy import deepcopy
import logging
from typing import Any, Dict

from ..const import (
    ATTR_IMAGE,
    ATTR_OPTIONS,
    ATTR_SYSTEM,
    ATTR_USER,
    ATTR_VERSION,
    FILE_HASSIO_ADDONS,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..utils.json import JsonConfig
from ..store.addon import AddonStore
from .addon import Addon
from .validate import SCHEMA_ADDONS_FILE

_LOGGER: logging.Logger = logging.getLogger(__name__)

Config = Dict[str, Any]


class AddonsData(JsonConfig, CoreSysAttributes):
    """Hold data for installed Add-ons inside Supervisor."""

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

    def install(self, addon: AddonStore) -> None:
        """Set addon as installed."""
        self.system[addon.slug] = deepcopy(addon.data)
        self.user[addon.slug] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: addon.version,
            ATTR_IMAGE: addon.image,
        }
        self.save_data()

    def uninstall(self, addon: Addon) -> None:
        """Set add-on as uninstalled."""
        self.system.pop(addon.slug, None)
        self.user.pop(addon.slug, None)
        self.save_data()

    def update(self, addon: AddonStore) -> None:
        """Update version of add-on."""
        self.system[addon.slug] = deepcopy(addon.data)
        self.user[addon.slug].update(
            {ATTR_VERSION: addon.version, ATTR_IMAGE: addon.image}
        )
        self.save_data()

    def restore(self, slug: str, user: Config, system: Config, image: str) -> None:
        """Restore data to add-on."""
        self.user[slug] = deepcopy(user)
        self.system[slug] = deepcopy(system)

        self.user[slug][ATTR_IMAGE] = image
        self.save_data()
