"""Home Assistant control object."""
import asyncio
from collections.abc import Awaitable
from contextlib import suppress
import logging
import re
import secrets
import shutil

import attr
from awesomeversion import AwesomeVersion

from ..const import ATTR_HOMEASSISTANT, BusEvent
from ..coresys import CoreSys
from ..docker.const import ContainerState
from ..docker.homeassistant import DockerHomeAssistant
from ..docker.monitor import DockerContainerStateEvent
from ..docker.stats import DockerStats
from ..exceptions import (
    DockerError,
    HomeAssistantCrashError,
    HomeAssistantError,
    HomeAssistantJobError,
    HomeAssistantUpdateError,
    JobException,
)
from ..jobs.const import JOB_GROUP_HOME_ASSISTANT_CORE, JobExecutionLimit
from ..jobs.decorator import Job, JobCondition
from ..jobs.job_group import JobGroup
from ..resolution.const import ContextType, IssueType
from ..utils import convert_to_ascii
from ..utils.sentry import capture_exception
from .const import (
    LANDINGPAGE,
    WATCHDOG_MAX_ATTEMPTS,
    WATCHDOG_RETRY_SECONDS,
    WATCHDOG_THROTTLE_MAX_CALLS,
    WATCHDOG_THROTTLE_PERIOD,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")


@attr.s(frozen=True)
class ConfigResult:
    """Return object from config check."""

    valid = attr.ib()
    log = attr.ib()


class HomeAssistantCore(JobGroup):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        super().__init__(coresys, JOB_GROUP_HOME_ASSISTANT_CORE)
        self.instance: DockerHomeAssistant = DockerHomeAssistant(coresys)
        self.lock: asyncio.Lock = asyncio.Lock()
        self._error_state: bool = False

    @property
    def error_state(self) -> bool:
        """Return True if system is in error."""
        return self._error_state

    async def load(self) -> None:
        """Prepare Home Assistant object."""
        self.sys_bus.register_event(
            BusEvent.DOCKER_CONTAINER_STATE_CHANGE, self.watchdog_container
        )

        try:
            # Evaluate Version if we lost this information
            if not self.sys_homeassistant.version:
                self.sys_homeassistant.version = (
                    await self.instance.get_latest_version()
                )

            await self.instance.attach(version=self.sys_homeassistant.version)
        except DockerError:
            _LOGGER.info(
                "No Home Assistant Docker image %s found.", self.sys_homeassistant.image
            )
            await self.install_landingpage()
        else:
            self.sys_homeassistant.version = self.instance.version
            self.sys_homeassistant.image = self.instance.image
            self.sys_homeassistant.save_data()

        # Start landingpage
        if self.instance.version != LANDINGPAGE:
            return

        _LOGGER.info("Starting HomeAssistant landingpage")
        if not await self.instance.is_running():
            with suppress(HomeAssistantError):
                await self.start()

    @Job(
        name="home_assistant_core_install_landing_page",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def install_landingpage(self) -> None:
        """Install a landing page."""
        # Try to use a preinstalled landingpage
        try:
            await self.instance.attach(version=LANDINGPAGE)
        except DockerError:
            pass
        else:
            _LOGGER.info("Using preinstalled landingpage")
            self.sys_homeassistant.version = LANDINGPAGE
            self.sys_homeassistant.image = self.instance.image
            self.sys_homeassistant.save_data()
            return

        _LOGGER.info("Setting up Home Assistant landingpage")
        while True:
            if not self.sys_updater.image_homeassistant:
                _LOGGER.warning(
                    "Found no information about Home Assistant. Retry in 30sec"
                )
                await asyncio.sleep(30)
                await self.sys_updater.reload()
                continue

            try:
                await self.instance.install(
                    LANDINGPAGE, image=self.sys_updater.image_homeassistant
                )
                break
            except (DockerError, JobException):
                pass
            except Exception as err:  # pylint: disable=broad-except
                capture_exception(err)

            _LOGGER.warning("Fails install landingpage, retry after 30sec")
            await asyncio.sleep(30)

        self.sys_homeassistant.version = LANDINGPAGE
        self.sys_homeassistant.image = self.sys_updater.image_homeassistant
        self.sys_homeassistant.save_data()

    @Job(
        name="home_assistant_core_install",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def install(self) -> None:
        """Install a landing page."""
        _LOGGER.info("Home Assistant setup")
        while True:
            # read homeassistant tag and install it
            if not self.sys_homeassistant.latest_version:
                await self.sys_updater.reload()

            if self.sys_homeassistant.latest_version:
                try:
                    await self.instance.update(
                        self.sys_homeassistant.latest_version,
                        image=self.sys_updater.image_homeassistant,
                    )
                    break
                except (DockerError, JobException):
                    pass
                except Exception as err:  # pylint: disable=broad-except
                    capture_exception(err)

            _LOGGER.warning("Error on Home Assistant installation. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Home Assistant docker now installed")
        self.sys_homeassistant.version = self.instance.version
        self.sys_homeassistant.image = self.sys_updater.image_homeassistant
        self.sys_homeassistant.save_data()

        # finishing
        try:
            _LOGGER.info("Starting Home Assistant")
            await self.start()
        except HomeAssistantError:
            _LOGGER.error("Can't start Home Assistant!")

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup()

    @Job(
        name="home_assistant_core_update",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.PLUGINS_UPDATED,
            JobCondition.SUPERVISOR_UPDATED,
        ],
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def update(
        self,
        version: AwesomeVersion | None = None,
        backup: bool | None = False,
    ) -> None:
        """Update HomeAssistant version."""
        version = version or self.sys_homeassistant.latest_version
        old_image = self.sys_homeassistant.image
        rollback = self.sys_homeassistant.version if not self.error_state else None
        running = await self.instance.is_running()
        exists = await self.instance.exists()

        if exists and version == self.instance.version:
            raise HomeAssistantUpdateError(
                f"Version {version!s} is already installed", _LOGGER.warning
            )

        if backup:
            await self.sys_backups.do_backup_partial(
                name=f"core_{self.instance.version}",
                homeassistant=True,
                folders=[ATTR_HOMEASSISTANT],
            )

        # process an update
        async def _update(to_version: AwesomeVersion) -> None:
            """Run Home Assistant update."""
            _LOGGER.info("Updating Home Assistant to version %s", to_version)
            try:
                await self.instance.update(
                    to_version, image=self.sys_updater.image_homeassistant
                )
            except DockerError as err:
                raise HomeAssistantUpdateError(
                    "Updating Home Assistant image failed", _LOGGER.warning
                ) from err

            self.sys_homeassistant.version = self.instance.version
            self.sys_homeassistant.image = self.sys_updater.image_homeassistant

            if running:
                await self.start()
            _LOGGER.info("Successfully started Home Assistant %s", to_version)

            # Successfull - last step
            self.sys_homeassistant.save_data()
            with suppress(DockerError):
                await self.instance.cleanup(old_image=old_image)

        # Update Home Assistant
        with suppress(HomeAssistantError):
            await _update(version)

        if not self.error_state and rollback:
            try:
                data = await self.sys_homeassistant.api.get_config()
            except HomeAssistantError:
                # The API stoped responding between the up checks an now
                self._error_state = True
                data = None

            # Verify that the frontend is loaded
            if data and "frontend" not in data.get("components", []):
                _LOGGER.error("API responds but frontend is not loaded")
                self._error_state = True
            else:
                return

        # Update going wrong, revert it
        if self.error_state and rollback:
            _LOGGER.critical("HomeAssistant update failed -> rollback!")
            self.sys_resolution.create_issue(
                IssueType.UPDATE_ROLLBACK, ContextType.CORE
            )

            # Make a copy of the current log file if it exists
            logfile = self.sys_config.path_homeassistant / "home-assistant.log"
            if logfile.exists():
                backup = (
                    self.sys_config.path_homeassistant / "home-assistant-rollback.log"
                )

                shutil.copy(logfile, backup)
                _LOGGER.info(
                    "A backup of the logfile is stored in /config/home-assistant-rollback.log"
                )
            await _update(rollback)
        else:
            self.sys_resolution.create_issue(IssueType.UPDATE_FAILED, ContextType.CORE)
            raise HomeAssistantUpdateError()

    @Job(
        name="home_assistant_core_start",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def start(self) -> None:
        """Run Home Assistant docker."""
        if await self.instance.is_running():
            _LOGGER.warning("Home Assistant is already running!")
            return

        # Instance/Container exists, simple start
        if await self.instance.is_initialize():
            try:
                await self.instance.start()
            except DockerError as err:
                raise HomeAssistantError() from err

            await self._block_till_run(self.sys_homeassistant.version)
        # No Instance/Container found, extended start
        else:
            # Create new API token
            self.sys_homeassistant.supervisor_token = secrets.token_hex(56)
            self.sys_homeassistant.save_data()

            # Write audio settings
            self.sys_homeassistant.write_pulse()

            try:
                await self.instance.run()
            except DockerError as err:
                raise HomeAssistantError() from err

            await self._block_till_run(self.sys_homeassistant.version)

    @Job(
        name="home_assistant_core_stop",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def stop(self) -> None:
        """Stop Home Assistant Docker."""
        try:
            return await self.instance.stop(remove_container=False)
        except DockerError as err:
            raise HomeAssistantError() from err

    @Job(
        name="home_assistant_core_restart",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def restart(self) -> None:
        """Restart Home Assistant Docker."""
        try:
            await self.instance.restart()
        except DockerError as err:
            raise HomeAssistantError() from err

        await self._block_till_run(self.sys_homeassistant.version)

    @Job(
        name="home_assistant_core_rebuild",
        limit=JobExecutionLimit.GROUP_ONCE,
        on_condition=HomeAssistantJobError,
    )
    async def rebuild(self) -> None:
        """Rebuild Home Assistant Docker container."""
        with suppress(DockerError):
            await self.instance.stop()
        await self.start()

    def logs(self) -> Awaitable[bytes]:
        """Get HomeAssistant docker logs.

        Return a coroutine.
        """
        return self.instance.logs()

    def check_trust(self) -> Awaitable[None]:
        """Calculate HomeAssistant docker content trust.

        Return Coroutine.
        """
        return self.instance.check_trust()

    async def stats(self) -> DockerStats:
        """Return stats of Home Assistant."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise HomeAssistantError() from err

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

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress or self.lock.locked()

    async def check_config(self) -> ConfigResult:
        """Run Home Assistant config check."""
        try:
            result = await self.instance.execute_command(
                "python3 -m homeassistant -c /config --script check_config"
            )
        except DockerError as err:
            raise HomeAssistantError() from err

        # If not valid
        if result.exit_code is None:
            raise HomeAssistantError("Fatal error on config check!", _LOGGER.error)

        # Convert output
        log = convert_to_ascii(result.output)
        _LOGGER.debug("Result config check: %s", log.strip())

        # Parse output
        if result.exit_code != 0 or RE_YAML_ERROR.search(log):
            _LOGGER.error("Invalid Home Assistant config found!")
            return ConfigResult(False, log)

        _LOGGER.info("Home Assistant config is valid")
        return ConfigResult(True, log)

    async def _block_till_run(self, version: AwesomeVersion) -> None:
        """Block until Home-Assistant is booting up or startup timeout."""
        # Skip landingpage
        if version == LANDINGPAGE:
            return
        _LOGGER.info("Wait until Home Assistant is ready")

        while True:
            await asyncio.sleep(5)

            # 1: Check if Container is is_running
            if not await self.instance.is_running():
                _LOGGER.error("Home Assistant has crashed!")
                break

            # 2: Check if API response
            if await self.sys_homeassistant.api.check_api_state():
                _LOGGER.info("Detect a running Home Assistant instance")
                self._error_state = False
                return

        self._error_state = True
        raise HomeAssistantCrashError()

    @Job(
        name="home_assistant_core_repair",
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
        ],
    )
    async def repair(self):
        """Repair local Home Assistant data."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repair Home Assistant %s", self.sys_homeassistant.version)
        try:
            await self.instance.install(self.sys_homeassistant.version)
        except DockerError:
            _LOGGER.error("Repairing of Home Assistant failed")

    async def watchdog_container(self, event: DockerContainerStateEvent) -> None:
        """Process state changes in Home Assistant container and restart if necessary."""
        if not (event.name == self.instance.name and self.sys_homeassistant.watchdog):
            return

        if event.state in [ContainerState.FAILED, ContainerState.UNHEALTHY]:
            await self._restart_after_problem(event.state)

    @Job(
        name="home_assistant_core_restart_after_problem",
        limit=JobExecutionLimit.THROTTLE_RATE_LIMIT,
        throttle_period=WATCHDOG_THROTTLE_PERIOD,
        throttle_max_calls=WATCHDOG_THROTTLE_MAX_CALLS,
    )
    async def _restart_after_problem(self, state: ContainerState):
        """Restart unhealthy or failed Home Assistant."""
        attempts = 0
        while await self.instance.current_state() == state:
            # Don't interrupt a task in progress or if rollback is handling it
            if not (self.in_progress or self.error_state):
                _LOGGER.warning(
                    "Watchdog found Home Assistant %s, restarting...", state.value
                )
                if state == ContainerState.FAILED and attempts == 0:
                    try:
                        await self.start()
                    except HomeAssistantError as err:
                        capture_exception(err)
                    else:
                        break

                try:
                    if state == ContainerState.FAILED:
                        await self.rebuild()
                    else:
                        await self.restart()
                except HomeAssistantError as err:
                    attempts = attempts + 1
                    _LOGGER.error("Watchdog restart of Home Assistant failed!")
                    capture_exception(err)
                else:
                    break

            if attempts >= WATCHDOG_MAX_ATTEMPTS:
                _LOGGER.critical(
                    "Watchdog cannot restart Home Assistant, failed all %s attempts",
                    attempts,
                )
                break

            await asyncio.sleep(WATCHDOG_RETRY_SECONDS)
