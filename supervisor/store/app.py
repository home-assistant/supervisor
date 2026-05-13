"""Init file for Supervisor apps."""

from copy import deepcopy
import logging
from typing import Self

from ..apps.model import AppModel, Data
from ..coresys import CoreSys

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AppStore(AppModel):
    """Hold data for app inside Supervisor."""

    def __init__(self, coresys: CoreSys, slug: str, data: Data | None = None):
        """Initialize object."""
        super().__init__(coresys, slug)
        self._data: Data | None = data

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Store: {self.slug}>"

    @property
    def data(self) -> Data:
        """Return app data/config."""
        return self._data or self.sys_store.data.apps[self.slug]

    @property
    def is_installed(self) -> bool:
        """Return True if an app is installed."""
        return self.sys_apps.get_local_only(self.slug) is not None

    @property
    def is_detached(self) -> bool:
        """Return True if app is detached."""
        return False

    def clone(self) -> Self:
        """Return a copy that includes data and does not use global store data."""
        return type(self)(self.coresys, self.slug, deepcopy(self.data))
