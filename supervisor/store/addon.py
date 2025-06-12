"""Init file for Supervisor add-ons."""

from copy import deepcopy
import logging
from typing import Self

from ..addons.model import AddonModel, Data
from ..coresys import CoreSys

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AddonStore(AddonModel):
    """Hold data for add-on inside Supervisor."""

    def __init__(self, coresys: CoreSys, slug: str, data: Data | None = None):
        """Initialize object."""
        super().__init__(coresys, slug)
        self._data: Data | None = data

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Store: {self.slug}>"

    @property
    def data(self) -> Data:
        """Return add-on data/config."""
        return self._data or self.sys_store.data.addons[self.slug]

    @property
    def is_installed(self) -> bool:
        """Return True if an add-on is installed."""
        return self.sys_addons.get_local_only(self.slug) is not None

    @property
    def is_detached(self) -> bool:
        """Return True if add-on is detached."""
        return False

    def clone(self) -> Self:
        """Return a copy that includes data and does not use global store data."""
        return type(self)(self.coresys, self.slug, deepcopy(self.data))
