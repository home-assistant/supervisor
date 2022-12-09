"""Supervisor plugins base class."""
from abc import ABC, abstractmethod
import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import logging

from awesomeversion import AwesomeVersion, AwesomeVersionException

from ..const import ATTR_IMAGE, ATTR_VERSION, BusEvent
from ..coresys import CoreSysAttributes
from ..docker.const import ContainerState
from ..docker.interface import DockerInterface
from ..docker.monitor import DockerContainerStateEvent
from ..exceptions import DockerError, PluginError
from ..utils.common import FileConfiguration
from ..utils.sentry import capture_exception
from .const import WATCHDOG_MAX_ATTEMPTS, WATCHDOG_RETRY_SECONDS

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginBase(ABC, FileConfiguration, CoreSysAttributes):
    """Base class for plugins."""

    slug: str
    instance: DockerInterface

    @property
    def version(self) -> AwesomeVersion | None:
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
    def latest_version(self) -> AwesomeVersion | None:
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

    def start_watchdog(self) -> None:
        """Register docker container listener for plugin."""
        self.sys_bus.register_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE, self.watchdog_container
        )

    async def watchdog_container(self, event: DockerContainerStateEvent) -> None:
        """Process state changes in plugin container and restart if necessary."""
        if not (event.name == self.instance.name):
            return

        if event.state in [
            ContainerState.FAILED,
            ContainerState.STOPPED,
            ContainerState.UNHEALTHY,
        ]:
            await self._restart_after_problem(event.state)

    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed plugin."""
        attempts = 0
        while await self.instance.current_state() == state:
            if not self.in_progress:
                _LOGGER.warning(
                    "Watchdog found %s plugin %s, restarting...",
                    self.slug,
                    state.value,
                )
                try:
                    if state == ContainerState.STOPPED and attempts == 0:
                        await self.start()
                    else:
                        await self.rebuild()
                except PluginError as err:
                    attempts = attempts + 1
                    _LOGGER.error("Watchdog restart of %s plugin failed!", self.slug)
                    capture_exception(err)
                else:
                    break

            if attempts >= WATCHDOG_MAX_ATTEMPTS:
                _LOGGER.critical(
                    "Watchdog cannot restart %s plugin, failed all %s attempts",
                    self.slug,
                    attempts,
                )
                break

            await asyncio.sleep(WATCHDOG_RETRY_SECONDS)

    async def rebuild(self) -> None:
        """Rebuild system plugin."""
        with suppress(DockerError):
            await self.instance.stop()
        await self.start()

    @abstractmethod
    async def start(self) -> None:
        """Start system plugin."""

    async def load(self) -> None:
        """Load system plugin."""
        self.start_watchdog()

        # Check plugin state
        try:
            # Evaluate Version if we lost this information
            if not self.version:
                self.version = await self.instance.get_latest_version()

            await self.instance.attach(
                version=self.version, skip_state_event_if_down=True
            )
        except DockerError:
            _LOGGER.info(
                "No %s plugin Docker image %s found.", self.slug, self.instance.image
            )

            # Install plugin
            with suppress(PluginError):
                await self.install()
        else:
            self.version = self.instance.version
            self.image = self.instance.image
            self.save_data()

        # Run plugin
        with suppress(PluginError):
            if not await self.instance.is_running():
                await self.start()

    @abstractmethod
    async def install(self) -> None:
        """Install system plugin."""

    @abstractmethod
    async def update(self, version: str | None = None) -> None:
        """Update system plugin."""

    @abstractmethod
    async def repair(self) -> None:
        """Repair system plugin."""
