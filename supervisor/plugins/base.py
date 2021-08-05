"""Supervisor plugins base class."""
from abc import ABC, abstractmethod
from typing import Optional

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ..const import ATTR_IMAGE, ATTR_VERSION
from ..coresys import CoreSysAttributes
from ..utils.common import FileConfiguration


class PluginBase(ABC, FileConfiguration, CoreSysAttributes):
    """Base class for plugins."""

    slug: str = ""

    @property
    def version(self) -> Optional[AwesomeVersion]:
        """Return current version of the plugin."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: AwesomeVersion) -> None:
        """Set current version of the plugin."""
        self._data[ATTR_VERSION] = value

    @property
    def image(self) -> str:
        """Return current image of plugin."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return f"ghcr.io/home-assistant/{self.sys_arch.supervisor}-hassio-{self.slug}"

    @image.setter
    def image(self, value: str) -> None:
        """Return current image of the plugin."""
        self._data[ATTR_IMAGE] = value

    @property
    @abstractmethod
    def latest_version(self) -> Optional[AwesomeVersion]:
        """Return latest version of the plugin."""

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        try:
            return self.version < self.latest_version
        except (AwesomeVersionException, TypeError):
            return False

    @abstractmethod
    async def load(self) -> None:
        """Load system plugin."""

    @abstractmethod
    async def install(self) -> None:
        """Install system plugin."""

    @abstractmethod
    async def update(self, version: Optional[str] = None) -> None:
        """Update system plugin."""

    @abstractmethod
    async def repair(self) -> None:
        """Repair system plugin."""
