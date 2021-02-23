"""Init file for Supervisor add-ons."""
import logging
from typing import Optional

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ..addons.model import AddonModel, Data
from ..const import ATTR_ARCH, ATTR_HOMEASSISTANT, ATTR_MACHINE

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

    @property
    def available_arch(self) -> bool:
        """Return True if the running arch is supported by the add-on."""
        return self._available_arch(self.data)

    @property
    def available_homeassistant(self) -> bool:
        """Return True if the running version of Home Assistant is supported by the add-on."""
        return self._available_homeassistant(self.data)

    @property
    def available(self) -> bool:
        """Return True if this add-on is available on this platform."""
        return self._available(self.data)

    def _available_arch(self, config) -> bool:
        """Return True if the running arch is supported by the add-on."""
        # Architecture
        if not self.sys_arch.is_supported(config[ATTR_ARCH]):
            return False

        # Machine / Hardware
        machine = config.get(ATTR_MACHINE)
        if machine and f"!{self.sys_machine}" in machine:
            return False
        elif machine and self.sys_machine not in machine:
            return False

        return True

    def _available_homeassistant(self, config) -> bool:
        """Return True if the running version of Home Assistant is supported by the add-on."""
        version: Optional[AwesomeVersion] = config.get(ATTR_HOMEASSISTANT)
        try:
            return self.sys_homeassistant.version >= version
        except (AwesomeVersionException, TypeError):
            return True

    def _available(self, config) -> bool:
        """Return True if this add-on is available on this platform."""
        return self._available_arch(config) and self._available_homeassistant(config)
