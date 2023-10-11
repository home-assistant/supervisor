"""Init file for Supervisor add-ons."""

from copy import deepcopy
import logging

from ..addons.model import AddonModel, Data

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AddonStore(AddonModel):
    """Hold data for add-on inside Supervisor."""

    _data: Data | None = None

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
        return self.sys_addons.get(self.slug, local_only=True) is not None

    @property
    def is_detached(self) -> bool:
        """Return True if add-on is detached."""
        return False

    def clone(self) -> "AddonStore":
        """Return a copy that includes data and does not use global store data."""
        addon = AddonStore(self.coresys, self.slug)
        addon._data = deepcopy(self.data)
        return addon
