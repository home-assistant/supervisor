"""Supervisor plugins base class."""
from abc import ABC, abstractmethod
from typing import Awaitable, Optional

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ..const import ATTR_IMAGE, ATTR_VERSION
from ..coresys import CoreSysAttributes
from ..docker.interface import DockerInterface
from ..utils.common import FileConfiguration


class PluginBase(ABC, FileConfiguration, CoreSysAttributes):
    """Base class for plugins."""

    slug: str
    instance: DockerInterface

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

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    def check_trust(self) -> Awaitable[None]:
        """Calculate plugin docker content trust.

        Return Coroutine.
        """
        return self.instance.check_trust()

    def logs(self) -> Awaitable[bytes]:
        """Get docker plugin logs.

        Return Coroutine.
        """
        return self.instance.logs()

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    def is_failed(self) -> Awaitable[bool]:
        """Return True if a Docker container is failed state.

        Return a coroutine.
        """
        return self.instance.is_failed()

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
