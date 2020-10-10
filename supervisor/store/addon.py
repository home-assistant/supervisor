"""Init file for Supervisor add-ons."""
import logging

from ..addons.model import AddonModel, Data

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AddonStore(AddonModel):
    """Hold data for add-on inside Supervisor."""

    def __repr__(self) -> str:
        """Return internal representation."""
        return f"<Store: {self.slug}>"

    @property
    def data(self) -> Data:
        """Return add-on data/config."""
        return self.sys_store.data.addons[self.slug]

    @property
    def is_installed(self) -> bool:
        """Return True if an add-on is installed."""
        return False

    @property
    def is_detached(self) -> bool:
        """Return True if add-on is detached."""
        return False
