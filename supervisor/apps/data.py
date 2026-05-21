"""Init file for Supervisor app data."""

from copy import deepcopy
from typing import Any

from ..const import (
    ATTR_IMAGE,
    ATTR_OPTIONS,
    ATTR_SYSTEM,
    ATTR_USER,
    ATTR_VERSION,
    FILE_HASSIO_APPS,
)
from ..coresys import CoreSys, CoreSysAttributes
from ..store.app import AppStore
from ..utils.common import FileConfiguration
from .app import App
from .validate import SCHEMA_ADDONS_FILE

Config = dict[str, Any]


class AppsData(FileConfiguration, CoreSysAttributes):
    """Hold data for installed Apps inside Supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize data holder."""
        super().__init__(FILE_HASSIO_APPS, SCHEMA_ADDONS_FILE)
        self.coresys: CoreSys = coresys

    @property
    def user(self):
        """Return local app user data."""
        return self._data[ATTR_USER]

    @property
    def system(self):
        """Return local app data."""
        return self._data[ATTR_SYSTEM]

    async def install(self, app: AppStore) -> None:
        """Set app as installed."""
        self.system[app.slug] = deepcopy(app.data)
        self.user[app.slug] = {
            ATTR_OPTIONS: {},
            ATTR_VERSION: app.version,
            ATTR_IMAGE: app.image,
        }
        await self.save_data()

    async def uninstall(self, app: App) -> None:
        """Set app as uninstalled."""
        self.system.pop(app.slug, None)
        self.user.pop(app.slug, None)
        await self.save_data()

    async def update(self, app: AppStore) -> None:
        """Update version of app."""
        self.system[app.slug] = deepcopy(app.data)
        self.user[app.slug].update({ATTR_VERSION: app.version, ATTR_IMAGE: app.image})
        await self.save_data()

    async def restore(
        self, slug: str, user: Config, system: Config, image: str
    ) -> None:
        """Restore data to app."""
        self.user[slug] = deepcopy(user)
        self.system[slug] = deepcopy(system)

        self.user[slug][ATTR_IMAGE] = image
        await self.save_data()
