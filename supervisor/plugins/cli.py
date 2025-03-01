"""Home Assistant cli plugin.

Code: https://github.com/home-assistant/plugin-cli
"""

from collections.abc import Awaitable
import logging
import secrets

from awesomeversion import AwesomeVersion

from ..const import ATTR_ACCESS_TOKEN
from ..coresys import CoreSys
from ..docker.cli import DockerCli
from ..docker.const import ContainerState
from ..docker.stats import DockerStats
from ..exceptions import CliError, CliJobError, CliUpdateError, DockerError
from ..jobs.const import JobExecutionLimit
from ..jobs.decorator import Job
from ..utils.sentry import async_capture_exception
from .base import PluginBase
from .const import (
    FILE_HASSIO_CLI,
    PLUGIN_UPDATE_CONDITIONS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)
from .validate import SCHEMA_CLI_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginCli(PluginBase):
    """HA cli interface inside supervisor."""

    def __init__(self, coresys: CoreSys):
        """Initialize cli handler."""
        super().__init__(FILE_HASSIO_CLI, SCHEMA_CLI_CONFIG)
        self.slug = "cli"
        self.coresys: CoreSys = coresys
        self.instance: DockerCli = DockerCli(coresys)

    @property
    def default_image(self) -> str:
        """Return default image for cli plugin."""
        if self.sys_updater.image_cli:
            return self.sys_updater.image_cli
        return super().default_image

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return version of latest cli."""
        return self.sys_updater.version_cli

    @property
    def supervisor_token(self) -> str:
        """Return an access token for the Supervisor API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @Job(
        name="plugin_cli_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=CliJobError,
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update local HA cli."""
        try:
            await super().update(version)
        except DockerError as err:
            raise CliUpdateError("CLI update failed", _LOGGER.error) from err

    async def start(self) -> None:
        """Run cli."""
        # Create new API token
        self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        await self.save_data()

        # Start Instance
        _LOGGER.info("Starting CLI plugin")
        try:
            await self.instance.run()
        except DockerError as err:
            raise CliError("Can't start cli plugin", _LOGGER.error) from err

    async def stop(self) -> None:
        """Stop cli."""
        _LOGGER.info("Stopping cli plugin")
        try:
            await self.instance.stop()
        except DockerError as err:
            raise CliError("Can't stop cli plugin", _LOGGER.error) from err

    async def stats(self) -> DockerStats:
        """Return stats of cli."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise CliError() from err

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    async def repair(self) -> None:
        """Repair cli container."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing HA cli %s", self.version)
        try:
            await self.instance.install(self.version)
        except DockerError as err:
            _LOGGER.error("Repair of HA cli failed")
            await async_capture_exception(err)

    @Job(
        name="plugin_cli_restart_after_problem",
        limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=CliJobError,
    )
    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state)
