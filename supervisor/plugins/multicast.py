"""Home Assistant multicast plugin.

Code: https://github.com/home-assistant/plugin-multicast
"""

import logging

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys
from ..docker.const import ContainerState
from ..docker.multicast import DockerMulticast
from ..docker.stats import DockerStats
from ..exceptions import (
    DockerError,
    MulticastError,
    MulticastJobError,
    MulticastUpdateError,
)
from ..jobs.const import JobExecutionLimit
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
    def default_image(self) -> str:
        """Return default image for multicast plugin."""
        if self.sys_updater.image_multicast:
            return self.sys_updater.image_multicast
        return super().default_image

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return latest version of Multicast."""
        return self.sys_updater.version_multicast

    @Job(
        name="plugin_multicast_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=MulticastJobError,
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update Multicast plugin."""
        try:
            await super().update(version)
        except DockerError as err:
            raise MulticastUpdateError(
                "Multicast update failed", _LOGGER.error
            ) from err

    async def restart(self) -> None:
        """Restart Multicast plugin."""
        _LOGGER.info("Restarting Multicast plugin")
        try:
            await self.instance.restart()
        except DockerError as err:
            raise MulticastError("Can't start Multicast plugin", _LOGGER.error) from err

    async def start(self) -> None:
        """Run Multicast."""
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

    async def stats(self) -> DockerStats:
        """Return stats of Multicast."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise MulticastError() from err

    async def repair(self) -> None:
        """Repair Multicast plugin."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing Multicast %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of Multicast failed")
            await async_capture_exception(err)

    @Job(
        name="plugin_multicast_restart_after_problem",
        limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=MulticastJobError,
    )
    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state)
