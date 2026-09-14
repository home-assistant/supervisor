"""Home Assistant multicast plugin.

Code: https://github.com/home-assistant/plugin-multicast
"""

from contextlib import suppress
import logging

from awesomeversion import AwesomeVersion

from ..const import ATTR_ENABLED, ATTR_VERSION
from ..coresys import CoreSys
from ..docker.const import ContainerState
from ..docker.monitor import DockerContainerStateEvent
from ..docker.multicast import DockerMulticast
from ..docker.stats import DockerStats
from ..exceptions import (
    DockerContainerNotFoundError,
    DockerContainerNotRunningError,
    DockerError,
    DockerStatsTimeoutError,
    MulticastDisabledError,
    MulticastError,
    MulticastJobError,
    MulticastNotRunningError,
    MulticastStatsTimeoutError,
    MulticastUnknownError,
    MulticastUpdateError,
    PluginError,
)
from ..jobs.const import JobThrottle
from ..jobs.decorator import Job
from ..utils.sentry import async_capture_exception
from .base import PluginBase
from .const import (
    FILE_HASSIO_MULTICAST,
    PLUGIN_UPDATE_CONDITIONS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)
from .validate import SCHEMA_MULTICAST_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginMulticast(PluginBase):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        super().__init__(FILE_HASSIO_MULTICAST, SCHEMA_MULTICAST_CONFIG)
        self.slug = "multicast"
        self.coresys: CoreSys = coresys
        self.instance: DockerMulticast = DockerMulticast(coresys)

    @property
    def enabled(self) -> bool:
        """Return True if the multicast plugin is enabled."""
        return self._data[ATTR_ENABLED]

    @property
    def need_update(self) -> bool:
        """Return True if an update is available and the plugin is enabled."""
        return self.enabled and super().need_update

    @property
    def default_image(self) -> str:
        """Return default image for multicast plugin."""
        if self.sys_updater.image_multicast:
            return self.sys_updater.image_multicast
        return super().default_image

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return latest version of Multicast."""
        return self.sys_updater.version_multicast

    async def load(self) -> None:
        """Load Multicast plugin."""
        if self.enabled:
            await super().load()
            return

        _LOGGER.info("Multicast plugin is disabled")
        # Keep the watchdog registered so the plugin can be enabled at runtime,
        # watchdog_container ignores events while disabled.
        self.start_watchdog()

        # A previous disable may not have finished removing the container and
        # image (Supervisor exit, Docker error), retry the cleanup.
        with suppress(MulticastError):
            await self._remove()

    async def watchdog_container(self, event: DockerContainerStateEvent) -> None:
        """Process state changes in plugin container and restart if necessary."""
        if not self.enabled:
            return
        await super().watchdog_container(event)

    @Job(
        name="plugin_multicast_enable",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=MulticastJobError,
    )
    async def enable(self) -> None:
        """Enable, install and start the Multicast plugin."""
        if self.enabled:
            return

        _LOGGER.info("Enabling Multicast plugin")
        self._data[ATTR_ENABLED] = True
        await self.save_data()

        await self.install()
        await self.start()

    async def disable(self) -> None:
        """Disable the Multicast plugin and remove its container and image."""
        if self.enabled:
            _LOGGER.info("Disabling Multicast plugin")
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
            raise MulticastError(
                "Can't remove Multicast plugin", _LOGGER.error
            ) from err

        # Removed from the system, forget the installed version so a later
        # enable installs the current one.
        if self.version:
            self._data.pop(ATTR_VERSION, None)
            await self.save_data()

    @Job(
        name="plugin_multicast_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=MulticastJobError,
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update Multicast plugin."""
        if not self.enabled:
            raise MulticastDisabledError(_LOGGER.error)
        try:
            await super().update(version)
        except (DockerError, PluginError) as err:
            raise MulticastUpdateError(
                "Multicast update failed", _LOGGER.error
            ) from err

    async def restart(self) -> None:
        """Restart Multicast plugin."""
        if not self.enabled:
            raise MulticastDisabledError(_LOGGER.error)
        _LOGGER.info("Restarting Multicast plugin")
        try:
            await self.instance.restart()
        except DockerError as err:
            raise MulticastError("Can't start Multicast plugin", _LOGGER.error) from err

    async def start(self) -> None:
        """Run Multicast."""
        if not self.enabled:
            raise MulticastDisabledError(_LOGGER.error)
        _LOGGER.info("Starting Multicast plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            raise MulticastError("Can't start Multicast plugin", _LOGGER.error) from err

    async def stop(self) -> None:
        """Stop Multicast."""
        _LOGGER.info("Stopping Multicast plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            raise MulticastError("Can't stop Multicast plugin", _LOGGER.error) from err

    async def stats(self, *, one_shot: bool = False) -> DockerStats:
        """Return stats of Multicast."""
        try:
            return await self.instance.stats(one_shot=one_shot)
        except (DockerContainerNotFoundError, DockerContainerNotRunningError) as err:
            raise MulticastNotRunningError(_LOGGER.warning) from err
        except DockerStatsTimeoutError as err:
            raise MulticastStatsTimeoutError(_LOGGER.error) from err
        except DockerError as err:
            _LOGGER.error("Could not get stats of container for Multicast: %s", err)
            raise MulticastUnknownError from err

    async def repair(self) -> None:
        """Repair Multicast plugin."""
        if not self.enabled or await self.instance.exists():
            return

        _LOGGER.info("Repairing Multicast %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of Multicast failed")
            await async_capture_exception(err)

    @Job(
        name="plugin_multicast_restart_after_problem",
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=MulticastJobError,
        throttle=JobThrottle.RATE_LIMIT,
    )
    async def _restart_after_problem(
        self, state: ContainerState, exit_code: int | None = None
    ):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state, exit_code)
