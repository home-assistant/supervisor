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
from ..exceptions import (
    CliDisabledError,
    CliJobError,
    CliNotInstalledError,
    CliNotRunningError,
    CliRestartError,
    CliStartError,
    CliStatsTimeoutError,
    CliStopError,
    CliUnknownError,
    CliUpdateAlreadyInstalledError,
    CliUpdateError,
)
from ..jobs.const import JobThrottle
from ..jobs.decorator import Job
from .base import PluginBase, PluginErrors
from .const import (
    FILE_HASSIO_CLI,
    OS_HOST_CLI_MIN_VERSION,
    PLUGIN_UPDATE_CONDITIONS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)
from .validate import SCHEMA_CLI_CONFIG

_LOGGER: logging.Logger = logging.getLogger(__name__)


class PluginCli(PluginBase):
    """HA cli interface inside supervisor."""

    errors = PluginErrors(
        start=CliStartError,
        stop=CliStopError,
        update=CliUpdateError,
        restart=CliRestartError,
        not_running=CliNotRunningError,
        stats_timeout=CliStatsTimeoutError,
        unknown=CliUnknownError,
        not_installed=CliNotInstalledError,
        already_installed=CliUpdateAlreadyInstalledError,
        disabled=CliDisabledError,
    )

    def __init__(self, coresys: CoreSys):
        """Initialize cli handler."""
        super().__init__(FILE_HASSIO_CLI, SCHEMA_CLI_CONFIG)
        self.slug = "cli"
        self.coresys: CoreSys = coresys
        self.instance: DockerCli = DockerCli(coresys)

    @property
    def enabled(self) -> bool:
        """Return True if the plugin is enabled and the host OS has no ha of its own."""
        return not self._host_has_cli() and super().enabled

    def _host_has_cli(self) -> bool:
        """Return True if the OS ships ha talking to the host OS socket."""
        return (
            OS_HOST_CLI_MIN_VERSION is not None
            and self.sys_os.available
            and self.sys_os.version is not None
            and self.sys_os.version >= OS_HOST_CLI_MIN_VERSION
        )

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
    def supervisor_token(self) -> str | None:
        """Return an access token for the Supervisor API."""
        return self._data.get(ATTR_ACCESS_TOKEN)

    @Job(
        name="plugin_cli_update",
        conditions=PLUGIN_UPDATE_CONDITIONS,
        on_condition=CliJobError,
    )
    async def update(self, version: str | None = None) -> None:
        """Update local HA cli."""
        await super().update(version)

    async def load(self) -> None:
        """Load the cli plugin and drop the token of a disabled one."""
        if not self.enabled and self._data.pop(ATTR_ACCESS_TOKEN, None):
            await self.save_data()
        await super().load()

    async def start(self) -> None:
        """Run cli with a new API token."""
        # The mount source must exist even when the host OS socket failed to bind
        try:
            await self.sys_run_in_executor(self.sys_host.ensure_run_dirs)
        except OSError as err:
            _LOGGER.error("Can't create socket folder for the cli: %s", err)
            raise CliStartError from err

        self._data[ATTR_ACCESS_TOKEN] = secrets.token_hex(56)
        await self.save_data()
        await super().start()

    def is_running(self) -> Awaitable[bool]:
        """Return True if Docker container is running.

        Return a coroutine.
        """
        return self.instance.is_running()

    @Job(
        name="plugin_cli_restart_after_problem",
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
        on_condition=CliJobError,
        throttle=JobThrottle.RATE_LIMIT,
    )
    async def _restart_after_problem(
        self, state: ContainerState, exit_code: int | None = None
    ):
        """Restart unhealthy or failed plugin."""
        return await super()._restart_after_problem(state, exit_code)
