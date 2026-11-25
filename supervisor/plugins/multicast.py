"""Home Assistant multicast plugin.

Code: https://github.com/home-assistant/plugin-multicast
"""

import logging

from awesomeversion import AwesomeVersion

from ..coresys import CoreSys
from ..docker.const import ContainerState
from ..docker.multicast import DockerMulticast
from ..exceptions import (
    DockerError,
    MulticastDisabledError,
    MulticastDisableError,
    MulticastEnableError,
    MulticastJobError,
    MulticastNotInstalledError,
    MulticastNotRunningError,
    MulticastRestartError,
    MulticastStartError,
    MulticastStatsTimeoutError,
    MulticastStopError,
    MulticastUnknownError,
    MulticastUpdateAlreadyInstalledError,
    MulticastUpdateError,
    PluginError,
)
from ..jobs.const import JobThrottle
from ..jobs.decorator import Job
from .base import PluginBase, PluginErrors
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

    errors = PluginErrors(
        start=MulticastStartError,
        stop=MulticastStopError,
        update=MulticastUpdateError,
        restart=MulticastRestartError,
        not_running=MulticastNotRunningError,
        stats_timeout=MulticastStatsTimeoutError,
        unknown=MulticastUnknownError,
        not_installed=MulticastNotInstalledError,
        already_installed=MulticastUpdateAlreadyInstalledError,
        disabled=MulticastDisabledError,
    )

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
        name="plugin_multicast_enable",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=MulticastJobError,
    )
    async def enable(self) -> None:
        """Enable, install and start the Multicast plugin."""
        try:
            await super().enable()
        except (DockerError, PluginError) as err:
            raise MulticastEnableError(_LOGGER.error) from err

    async def disable(self) -> None:
        """Disable the Multicast plugin and remove its container and image."""
        try:
            await super().disable()
        except (DockerError, PluginError) as err:
            raise MulticastDisableError(_LOGGER.error) from err

    @Job(
        name="plugin_multicast_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=MulticastJobError,
    )
    async def update(self, version: str | None = None) -> None:
        """Update Multicast plugin."""
        await super().update(version)

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
