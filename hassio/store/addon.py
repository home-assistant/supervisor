"""Init file for Hass.io add-ons."""
import logging
from typing import Any, Dict

from ..coresys import CoreSys
from ..addons.model import AddonModel

_LOGGER = logging.getLogger(__name__)


class Addon(AddonModel):
    """Hold data for add-on inside Hass.io."""

    def __init__(self, coresys: CoreSys, slug: str):
        """Initialize data holder."""
        self.coresys: CoreSys = coresys
        self.slug: str = slug

    @property
    def data(self) -> Dict[str, Any]:
        """Return add-on data/config."""
        return self.sys_store.data.addons[self.slug]
