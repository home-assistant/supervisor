"""Home Assistant control object."""
import asyncio
from contextlib import suppress
import logging
from pathlib import Path
import re
import secrets
import shutil
import time
from typing import Awaitable, Optional

import attr
from packaging import version as pkg_version

from ..coresys import CoreSys, CoreSysAttributes
from ..docker.homeassistant import DockerHomeAssistant
from ..docker.stats import DockerStats
from ..exceptions import (
    DockerError,
    HomeAssistantCrashError,
    HomeAssistantError,
    HomeAssistantUpdateError,
)
from ..jobs.decorator import Job, JobCondition
from ..resolution.const import ContextType, IssueType
from ..utils import convert_to_ascii, process_lock

_LOGGER: logging.Logger = logging.getLogger(__name__)

RE_YAML_ERROR = re.compile(r"homeassistant\.util\.yaml")

LANDINGPAGE: str = "landingpage"


@attr.s(frozen=True)
class ConfigResult:
    """Return object from config check."""

    valid = attr.ib()
    log = attr.ib()


class HomeAssistantCore(CoreSysAttributes):
    """Home Assistant core object for handle it."""

    def __init__(self, coresys: CoreSys):
        """Initialize Home Assistant object."""
        self.coresys: CoreSys = coresys
        self.instance: DockerHomeAssistant = DockerHomeAssistant(coresys)
        self.lock: asyncio.Lock = asyncio.Lock()
        self._error_state: bool = False

    @property
    def error_state(self) -> bool:
        """Return True if system is in error."""
        return self._error_state

    async def load(self) -> None:
        """Prepare Home Assistant object."""
        try:
            # Evaluate Version if we lost this information
            if not self.sys_homeassistant.version:
                self.sys_homeassistant.version = (
                    await self.instance.get_latest_version()
                )

            await self.instance.attach(tag=self.sys_homeassistant.version)
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
                await self._start()

    @process_lock
    async def install_landingpage(self) -> None:
        """Install a landing page."""
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
            except DockerError:
                _LOGGER.warning("Fails install landingpage, retry after 30sec")
                await asyncio.sleep(30)
            except Exception as err:  # pylint: disable=broad-except
                self.sys_capture_exception(err)
            else:
                self.sys_homeassistant.version = self.instance.version
                self.sys_homeassistant.image = self.sys_updater.image_homeassistant
                self.sys_homeassistant.save_data()
                break

    @process_lock
    async def install(self) -> None:
        """Install a landing page."""
        _LOGGER.info("Home Assistant setup")
        while True:
            # read homeassistant tag and install it
            if not self.sys_homeassistant.latest_version:
                await self.sys_updater.reload()

            tag = self.sys_homeassistant.latest_version
            if tag:
                try:
                    await self.instance.update(
                        tag, image=self.sys_updater.image_homeassistant
                    )
                    break
                except DockerError:
                    pass
                except Exception as err:  # pylint: disable=broad-except
                    self.sys_capture_exception(err)

            _LOGGER.warning("Error on Home Assistant installation. Retry in 30sec")
            await asyncio.sleep(30)

        _LOGGER.info("Home Assistant docker now installed")
        self.sys_homeassistant.version = self.instance.version
        self.sys_homeassistant.image = self.sys_updater.image_homeassistant
        self.sys_homeassistant.save_data()

        # finishing
        try:
            _LOGGER.info("Starting Home Assistant")
            await self._start()
        except HomeAssistantError:
            _LOGGER.error("Can't start Home Assistant!")

        # Cleanup
        with suppress(DockerError):
            await self.instance.cleanup()

    @process_lock
    @Job(
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
        ]
    )
    async def update(self, version: Optional[str] = None) -> None:
        """Update HomeAssistant version."""
        version = version or self.sys_homeassistant.latest_version
        old_image = self.sys_homeassistant.image
        rollback = self.sys_homeassistant.version if not self.error_state else None
        running = await self.instance.is_running()
        exists = await self.instance.exists()

        if exists and version == self.instance.version:
            _LOGGER.warning("Version %s is already installed", version)
            return

        # process an update
        async def _update(to_version: str) -> None:
            """Run Home Assistant update."""
            _LOGGER.info("Updating Home Assistant to version %s", to_version)
            try:
                await self.instance.update(
                    to_version, image=self.sys_updater.image_homeassistant
                )
            except DockerError as err:
                _LOGGER.warning("Updating Home Assistant image failed")
                raise HomeAssistantUpdateError() from err
            else:
                self.sys_homeassistant.version = self.instance.version
                self.sys_homeassistant.image = self.sys_updater.image_homeassistant

            if running:
                await self._start()
            _LOGGER.info("Successful started Home Assistant %s", to_version)

            # Successfull - last step
            self.sys_homeassistant.save_data()
            with suppress(DockerError):
                await self.instance.cleanup(old_image=old_image)

        # Update Home Assistant
        with suppress(HomeAssistantError):
            await _update(version)
            return

        # Update going wrong, revert it
        if self.error_state and rollback:
            _LOGGER.critical("HomeAssistant update failed -> rollback!")
            self.sys_resolution.create_issue(
                IssueType.UPDATE_ROLLBACK, ContextType.CORE
            )

            # Make a copy of the current log file if it exsist
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

    async def _start(self) -> None:
        """Start Home Assistant Docker & wait."""
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

    @process_lock
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
            await self._start()

    @process_lock
    async def stop(self) -> None:
        """Stop Home Assistant Docker.

        Return a coroutine.
        """
        try:
            return await self.instance.stop(remove_container=False)
        except DockerError as err:
            raise HomeAssistantError() from err

    @process_lock
    async def restart(self) -> None:
        """Restart Home Assistant Docker."""
        try:
            await self.instance.restart()
        except DockerError as err:
            raise HomeAssistantError() from err

        await self._block_till_run(self.sys_homeassistant.version)

    @process_lock
    async def rebuild(self) -> None:
        """Rebuild Home Assistant Docker container."""
        with suppress(DockerError):
            await self.instance.stop()
        await self._start()

    def logs(self) -> Awaitable[bytes]:
        """Get HomeAssistant docker logs.

        Return a coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of Home Assistant.

        Return a coroutine.
        """
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
        result = await self.instance.execute_command(
            "python3 -m homeassistant -c /config --script check_config"
        )

        # If not valid
        if result.exit_code is None:
            _LOGGER.error("Fatal error on config check!")
            raise HomeAssistantError()

        # Convert output
        log = convert_to_ascii(result.output)
        _LOGGER.debug("Result config check: %s", log.strip())

        # Parse output
        if result.exit_code != 0 or RE_YAML_ERROR.search(log):
            _LOGGER.error("Invalid Home Assistant config found!")
            return ConfigResult(False, log)

        _LOGGER.info("Home Assistant config is valid")
        return ConfigResult(True, log)

    async def _block_till_run(self, version: str) -> None:
        """Block until Home-Assistant is booting up or startup timeout."""
        # Skip landingpage
        if version == LANDINGPAGE:
            return
        _LOGGER.info("Wait until Home Assistant is ready")

        # Manage timeouts
        timeout: bool = True
        start_time = time.monotonic()
        with suppress(pkg_version.InvalidVersion):
            # Version provide early stage UI
            if pkg_version.parse(version) >= pkg_version.parse("0.112.0"):
                _LOGGER.debug("Disable startup timeouts - early UI")
                timeout = False

        # Database migration
        migration_progress = False
        migration_file = Path(self.sys_config.path_homeassistant, ".migration_progress")

        # PIP installation
        pip_progress = False
        pip_file = Path(self.sys_config.path_homeassistant, ".pip_progress")

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

            # 3: Running DB Migration
            if migration_file.exists():
                if not migration_progress:
                    migration_progress = True
                    _LOGGER.info("Home Assistant record migration in progress")
                continue
            if migration_progress:
                migration_progress = False  # Reset start time
                start_time = time.monotonic()
                _LOGGER.info("Home Assistant record migration done")

            # 4: Running PIP installation
            if pip_file.exists():
                if not pip_progress:
                    pip_progress = True
                    _LOGGER.info("Home Assistant pip installation in progress")
                continue
            if pip_progress:
                pip_progress = False  # Reset start time
                start_time = time.monotonic()
                _LOGGER.info("Home Assistant pip installation done")

            # 5: Timeout
            if (
                timeout
                and time.monotonic() - start_time > self.sys_homeassistant.wait_boot
            ):
                _LOGGER.warning("Don't wait anymore on Home Assistant startup!")
                break

        self._error_state = True
        raise HomeAssistantCrashError()

    @Job(
        conditions=[
            JobCondition.FREE_SPACE,
            JobCondition.INTERNET_HOST,
        ]
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
