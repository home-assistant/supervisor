"""Init file for Hass.io add-ons."""
import logging

from ..coresys import CoreSys
from ..addons.model import AddonModel, Data

_LOGGER: logging.Logger = logging.getLogger(__name__)


class AddonStore(AddonModel):
    """Hold data for add-on inside Hass.io."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.slug: str = slug

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
