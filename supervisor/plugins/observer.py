"""Home Assistant observer plugin.

Code: https://github.com/home-assistant/plugin-observer
"""

import logging
import secrets

import aiohttp
from awesomeversion import AwesomeVersion

from ..const import ATTR_ACCESS_TOKEN
from ..coresys import CoreSys
from ..docker.const import ContainerState
from ..docker.observer import DockerObserver
from ..exceptions import (
    ObserverJobError,
    ObserverNotInstalledError,
    ObserverNotRunningError,
    ObserverPortConflict,
    ObserverRestartError,
    ObserverStartError,
    ObserverStatsTimeoutError,
    ObserverUnknownError,
    ObserverUpdateAlreadyInstalledError,
    ObserverUpdateError,
)
from ..jobs.const import JobThrottle
from ..jobs.decorator import Job
from .base import PluginBase, PluginErrors
from .const import (
    FILE_HASSIO_OBSERVER,
    PLUGIN_UPDATE_CONDITIONS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)
from .validate import SCHEMA_OBSERVER_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginObserver(PluginBase):
    """Supervisor observer instance."""

    errors = PluginErrors(
        start=ObserverStartError,
        update=ObserverUpdateError,
        restart=ObserverRestartError,
        not_running=ObserverNotRunningError,
        stats_timeout=ObserverStatsTimeoutError,
        unknown=ObserverUnknownError,
        not_installed=ObserverNotInstalledError,
        already_installed=ObserverUpdateAlreadyInstalledError,
        port_conflict=ObserverPortConflict,
    )

    def __init__(self, coresys: CoreSys):
        """Initialize observer handler."""
        super().__init__(FILE_HASSIO_OBSERVER, SCHEMA_OBSERVER_CONFIG)
        self.slug = "observer"
        self.coresys: CoreSys = coresys
        self.instance: DockerObserver = DockerObserver(coresys)

    @property
    def default_image(self) -> str:
        """Return default image for observer plugin."""
        if self.sys_updater.image_observer:
            return self.sys_updater.image_observer
        return super().default_image

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return version of latest observer."""
        return self.sys_updater.version_observer

    @property
    def supervisor_token(self) -> str | None:
        """Return an access token for the Observer API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @Job(
        name="plugin_observer_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=ObserverJobError,
    )
    async def update(self, version: str | None = None) -> None:
        """Update local HA observer."""
        await super().update(version)

    async def start(self) -> None:
        """Run observer with a new API token."""
        self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        await self.save_data()
        await super().start()

    async def check_system_runtime(self) -> bool:
        """Check if the observer is running."""
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with self.sys_websession.get(
                f"http://{self.sys_docker.network.observer!s}/ping", timeout=timeout
            ) as request:
                if request.status == 200:
                    return True
        except aiohttp.ClientError, TimeoutError:
            pass

        return False

    @Job(
        name="plugin_observer_restart_after_problem",
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=ObserverJobError,
        throttle=JobThrottle.RATE_LIMIT,
    )
    async def _restart_after_problem(
        self, state: ContainerState, exit_code: int | None = None
    ):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state, exit_code)
