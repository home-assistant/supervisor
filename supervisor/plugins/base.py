"""Supervisor plugins base class."""

from abc import ABC, abstractmethod
import asyncio
from collections.abc import Awaitable, Callable, Coroutine
from contextlib import suppress
from dataclasses import dataclass
from functools import wraps
import logging
from pathlib import Path
from typing import Any, Concatenate

from awesomeversion import AwesomeVersion, AwesomeVersionException
import voluptuous as vol

from ..const import ATTR_ENABLED, ATTR_IMAGE, ATTR_VERSION, BusEvent
from ..coresys import CoreSysAttributes
from ..docker.const import ContainerState
from ..docker.interface import DockerInterface
from ..docker.monitor import DockerContainerStateEvent
from ..docker.stats import DockerStats
from ..exceptions import (
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerContainerPortConflict,
    DockerError,
    DockerStatsTimeoutError,
    PluginDisabledError,
    PluginError,
    PluginInstallError,
    PluginLatestVersionUnknownError,
    PluginNotInstalledError,
    PluginRemoveError,
    PluginUpdateAlreadyInstalledError,
)
from ..utils.common import FileConfiguration
from ..utils.sentry import async_capture_exception
from .const import WATCHDOG_MAX_ATTEMPTS, WATCHDOG_RETRY_SECONDS

_LOGGER: logging.Logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class PluginErrors:
    """Plugin specific error types raised by the shared plugin operations."""

    start: type[PluginError]
    update: type[PluginError]
    restart: type[PluginError]
    not_running: type[PluginError]
    stats_timeout: type[PluginError]
    unknown: type[PluginError]
    not_installed: type[PluginNotInstalledError]
    already_installed: type[PluginUpdateAlreadyInstalledError]
    disabled: type[PluginDisabledError] = PluginDisabledError
    port_conflict: type[PluginError] | None = None
    # None for a plugin that must not be stopped without a restart
    stop: type[PluginError] | None = None


def lifecycle_locked[T: PluginBase, **P, R](
    *, require_enabled: bool = True
) -> Callable[
    [Callable[Concatenate[T, P], Awaitable[R]]],
    Callable[Concatenate[T, P], Coroutine[Any, Any, R]],
]:
    """Serialize a plugin operation against the other lifecycle operations.

    The lock is not reentrant, a locked operation must not call another one.
    """

    def decorator(
        method: Callable[Concatenate[T, P], Awaitable[R]],
    ) -> Callable[Concatenate[T, P], Coroutine[Any, Any, R]]:
        @wraps(method)
        async def wrapper(self: T, *args: P.args, **kwargs: P.kwargs) -> R:
            async with self._lifecycle_lock:  # pylint: disable=protected-access
                if require_enabled and not self.enabled:
                    raise self.errors.disabled(logger=_LOGGER.error)
                return await method(self, *args, **kwargs)

        return wrapper

    return decorator


class PluginBase(ABC, FileConfiguration, CoreSysAttributes):
    """Base class for plugins."""

    slug: str
    instance: DockerInterface

    def __init__(self, file_path: Path, schema: vol.Schema) -> None:
        """Initialize plugin."""
        super().__init__(file_path, schema)
        self._lifecycle_lock = asyncio.Lock()

    @property
    @abstractmethod
    def errors(self) -> PluginErrors:
        """Return the plugin specific error types."""

    @property
    def version(self) -> AwesomeVersion | None:
        """Return current version of the plugin."""
        return self._data.get(ATTR_VERSION)

    @version.setter
    def version(self, value: AwesomeVersion) -> None:
        """Set current version of the plugin."""
        self._data[ATTR_VERSION] = value

    @property
    def enabled(self) -> bool:
        """Return True if the plugin is enabled."""
        return self._data.get(ATTR_ENABLED, True)

    @property
    def default_image(self) -> str:
        """Return default image for plugin."""
        return f"ghcr.io/home-assistant/{self.sys_arch.supervisor}-hassio-{self.slug}"

    @property
    def image(self) -> str:
        """Return current image of plugin."""
        if self._data.get(ATTR_IMAGE):
            return self._data[ATTR_IMAGE]
        return self.default_image

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
        """Return True if the plugin is enabled and an update is available."""
        try:
            return (
                self.enabled
                and self.version is not None
                and self.latest_version is not None
                and self.version < self.latest_version
            )
        except AwesomeVersionException, TypeError:
            return False

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

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
        if not self.enabled or event.name != self.instance.name:
            return

        if event.state in {ContainerState.FAILED, ContainerState.UNHEALTHY}:
            await self._restart_after_problem(event.state, event.exit_code)

    async def _restart_after_problem(
        self, state: ContainerState, exit_code: int | None = None
    ):
        """Restart unhealthy or failed plugin."""
        attempts = 0
        while self.enabled and await self.instance.current_state() == state:
            if not self.in_progress:
                if state == ContainerState.FAILED:
                    _LOGGER.warning(
                        "Watchdog found %s plugin exited with code %d, restarting...",
                        self.slug,
                        exit_code,
                    )
                else:
                    _LOGGER.warning(
                        "Watchdog found %s plugin %s, restarting...",
                        self.slug,
                        state,
                    )
                try:
                    await self.rebuild()
                except PluginError as err:
                    attempts = attempts + 1
                    _LOGGER.error("Watchdog restart of %s plugin failed!", self.slug)
                    await async_capture_exception(err)
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

    async def start(self) -> None:
        """Start system plugin."""
        if not self.enabled:
            raise self.errors.disabled(logger=_LOGGER.error)

        await self._write_config()
        _LOGGER.info("Starting %s plugin", self.slug)
        try:
            await self.instance.run()
        except DockerContainerPortConflict as err:
            error = self.errors.port_conflict or self.errors.start
            raise error(logger=_LOGGER.error) from err
        except DockerError as err:
            raise self.errors.start(logger=_LOGGER.error) from err

    async def stop(self) -> None:
        """Stop system plugin."""
        if not self.errors.stop:
            raise RuntimeError(
                f"Stopping {self.slug} plugin without a restart is not supported!"
            )

        _LOGGER.info("Stopping %s plugin", self.slug)
        try:
            await self.instance.stop()
        except DockerError as err:
            raise self.errors.stop(logger=_LOGGER.error) from err

    async def load(self) -> None:
        """Load system plugin."""
        # Registered even when disabled so the plugin can be enabled at runtime
        self.start_watchdog()

        if not self.enabled:
            _LOGGER.info("%s plugin is disabled", self.slug)
            # Retry the cleanup of a disable that did not finish
            with suppress(PluginError):
                await self._remove()
            return

        # Check plugin state
        try:
            # Evaluate Version if we lost this information
            if self.version:
                version = self.version
            else:
                self.version = version = await self.instance.get_latest_version()

            await self.instance.attach(version=version, skip_state_event_if_down=True)

            await self.instance.check_image(version, self.default_image)
        except DockerError:
            _LOGGER.info(
                "No %s plugin Docker image %s found.", self.slug, self.instance.image
            )

            # Install plugin
            with suppress(PluginError):
                await self.install()
        else:
            self.version = self.instance.version or version
            self.image = self.default_image
            await self.save_data()

        # Run plugin
        with suppress(PluginError):
            if not await self.instance.is_running():
                await self.start()

    async def install(self) -> None:
        """Install system plugin, retrying until it succeeds."""
        _LOGGER.info("Setup %s plugin", self.slug)
        while True:
            try:
                await self._install()
            except PluginError:
                _LOGGER.warning(
                    "Error on installing %s plugin, retrying in 30sec", self.slug
                )
                await asyncio.sleep(30)
            else:
                break

        _LOGGER.info("%s plugin now installed", self.slug)

    async def _install(self) -> None:
        """Install the latest version of the system plugin once."""
        if not self.latest_version:
            await self.sys_updater.reload()

        if not (to_version := self.latest_version):
            raise PluginLatestVersionUnknownError(plugin=self.slug)

        try:
            await self.instance.install(to_version, image=self.default_image)
        except DockerError as err:
            raise PluginInstallError(plugin=self.slug) from err

        self.version = self.instance.version or to_version
        self.image = self.default_image
        await self.save_data()

    @lifecycle_locked(require_enabled=False)
    async def enable(self) -> None:
        """Enable, install and start system plugin."""
        if self.enabled and await self.is_running():
            return

        if not self.enabled:
            # Finish the cleanup of a failed disable first
            if self.version:
                await self._remove()

            _LOGGER.info("Enabling %s plugin", self.slug)
            self._data[ATTR_ENABLED] = True
            await self.save_data()

        # Fail fast, the retrying install is only for boot
        if not self.version:
            await self._install()
        await self.start()

    @lifecycle_locked(require_enabled=False)
    async def disable(self) -> None:
        """Disable system plugin and remove its container and image."""
        if self.enabled:
            _LOGGER.info("Disabling %s plugin", self.slug)
            self._data[ATTR_ENABLED] = False
            await self.save_data()

        await self._remove()

    async def _remove(self) -> None:
        """Remove container and image of the plugin and forget the version."""
        try:
            await self.instance.stop()
            if self.version:
                await self.sys_docker.remove_image(self.image, self.version)
        except DockerError as err:
            raise PluginRemoveError(_LOGGER.error, plugin=self.slug) from err

        # Forget the version so a later enable installs the current one
        if self.version:
            self._data.pop(ATTR_VERSION, None)
            await self.save_data()

    @lifecycle_locked()
    async def update(self, version: str | None = None) -> None:
        """Update system plugin."""
        try:
            await self._update(version)
        except (DockerError, PluginError) as err:
            raise self.errors.update(logger=_LOGGER.error) from err

    async def _update(self, version: str | None) -> None:
        """Update the container of the system plugin and start it."""
        to_version = AwesomeVersion(version) if version else self.latest_version
        if not to_version:
            raise PluginLatestVersionUnknownError(_LOGGER.error, plugin=self.slug)

        old_image = self.image

        if to_version == self.version:
            _LOGGER.warning(
                "Version %s is already installed for %s", to_version, self.slug
            )
            return

        await self.instance.update(to_version, image=self.default_image)
        self.version = self.instance.version or to_version
        self.image = self.default_image
        await self.save_data()

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup(old_image=old_image)

        await self.start()

    async def _write_config(self) -> None:
        """Write the plugin configuration before its container (re)starts."""

    @lifecycle_locked()
    async def restart(self) -> None:
        """Restart system plugin."""
        _LOGGER.info("Restarting %s plugin", self.slug)
        await self._write_config()
        try:
            await self.instance.restart()
        except DockerError as err:
            raise self.errors.restart(logger=_LOGGER.error) from err

    async def stats(self, *, one_shot: bool = False) -> DockerStats:
        """Return stats of system plugin."""
        if not self.enabled:
            raise self.errors.disabled(logger=_LOGGER.warning)

        try:
            return await self.instance.stats(one_shot=one_shot)
        except (DockerContainerNotFoundError, DockerContainerNotRunningError) as err:
            raise self.errors.not_running(logger=_LOGGER.warning) from err
        except DockerStatsTimeoutError as err:
            raise self.errors.stats_timeout(logger=_LOGGER.error) from err
        except DockerError as err:
            _LOGGER.error(
                "Could not get stats of container for %s plugin: %s", self.slug, err
            )
            raise self.errors.unknown() from err

    @lifecycle_locked(require_enabled=False)
    async def repair(self) -> None:
        """Repair system plugin.

        Runs for all plugins as part of the system repair, so it never raises.
        A disabled plugin is left alone, it has no container to repair.
        """
        if not self.enabled or await self.instance.exists():
            return

        _LOGGER.info("Repairing %s plugin %s", self.slug, self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of %s plugin failed", self.slug)
            await async_capture_exception(err)
