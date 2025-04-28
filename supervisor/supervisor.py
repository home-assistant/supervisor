"""Home Assistant control object."""

from collections.abc import Awaitable
from contextlib import suppress
from datetime import timedelta
import errno
from ipaddress import IPv4Address
import logging
from pathlib import Path
from tempfile import TemporaryDirectory

import aiohttp
from aiohttp.client_exceptions import ClientError
from awesomeversion import AwesomeVersion, AwesomeVersionException

from .const import (
    ATTR_SUPERVISOR_INTERNET,
    SUPERVISOR_VERSION,
    URL_HASSIO_APPARMOR,
    BusEvent,
)
from .coresys import CoreSys, CoreSysAttributes
from .docker.stats import DockerStats
from .docker.supervisor import DockerSupervisor
from .exceptions import (
    CodeNotaryError,
    CodeNotaryUntrusted,
    DockerError,
    HostAppArmorError,
    SupervisorAppArmorError,
    SupervisorError,
    SupervisorJobError,
    SupervisorUpdateError,
)
from .jobs.const import JobCondition, JobExecutionLimit
from .jobs.decorator import Job
from .resolution.const import ContextType, IssueType, UnhealthyReason
from .utils.codenotary import calc_checksum
from .utils.sentry import async_capture_exception

_LOGGER: logging.Logger = logging.getLogger(__name__)


def _check_connectivity_throttle_period(coresys: CoreSys, *_) -> timedelta:
    """Throttle period for connectivity check."""
    if coresys.supervisor.connectivity:
        return timedelta(minutes=10)

    return timedelta(seconds=30)


class Supervisor(CoreSysAttributes):
    """Supervisor object."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        self.coresys: CoreSys = coresys
        self.instance: DockerSupervisor = DockerSupervisor(coresys)
        self._connectivity: bool = True

    async def load(self) -> None:
        """Prepare Supervisor object."""
        try:
            await self.instance.attach(version=self.version)
        except DockerError:
            _LOGGER.critical("Can't setup Supervisor Docker container!")

        with suppress(DockerError):
            await self.instance.cleanup(old_image=self.sys_config.image)

    @property
    def connectivity(self) -> bool:
        """Return true if we are connected to the internet."""
        return self._connectivity

    @connectivity.setter
    def connectivity(self, state: bool) -> None:
        """Set supervisor connectivity state."""
        if self._connectivity == state:
            return
        self._connectivity = state
        self.sys_bus.fire_event(BusEvent.SUPERVISOR_CONNECTIVITY_CHANGE, state)
        self.sys_homeassistant.websocket.supervisor_update_event(
            "network", {ATTR_SUPERVISOR_INTERNET: state}
        )

    @property
    def ip_address(self) -> IPv4Address:
        """Return IP of Supervisor instance."""
        return self.instance.ip_address

    @property
    def need_update(self) -> bool:
        """Return True if an update is available."""
        if self.sys_dev:
            return False

        try:
            return self.version < self.latest_version
        except (AwesomeVersionException, TypeError):
            return False

    @property
    def version(self) -> AwesomeVersion:
        """Return version of running Home Assistant."""
        return AwesomeVersion(SUPERVISOR_VERSION)

    @property
    def latest_version(self) -> AwesomeVersion:
        """Return last available version of Home Assistant."""
        return self.sys_updater.version_supervisor

    @property
    def image(self) -> str:
        """Return image name of Home Assistant container."""
        return self.instance.image

    @property
    def arch(self) -> str:
        """Return arch of the Supervisor container."""
        return self.instance.arch

    async def update_apparmor(self) -> None:
        """Fetch last version and update profile."""
        url = URL_HASSIO_APPARMOR.format(channel=self.sys_updater.channel)

        # Fetch
        try:
            _LOGGER.info("Fetching AppArmor profile %s", url)
            timeout = aiohttp.ClientTimeout(total=10)
            async with self.sys_websession.get(url, timeout=timeout) as request:
                if request.status != 200:
                    raise SupervisorAppArmorError(
                        f"Fetching AppArmor Profile from {url} response with {request.status}",
                        _LOGGER.error,
                    )
                data = await request.text()

        except (aiohttp.ClientError, TimeoutError) as err:
            self.sys_supervisor.connectivity = False
            raise SupervisorAppArmorError(
                f"Can't fetch AppArmor profile {url}: {str(err) or 'Timeout'}",
                _LOGGER.error,
            ) from err

        # Validate
        try:
            await self.sys_security.verify_own_content(calc_checksum(data))
        except CodeNotaryUntrusted as err:
            raise SupervisorAppArmorError(
                "Content-Trust is broken for the AppArmor profile fetch!",
                _LOGGER.critical,
            ) from err
        except CodeNotaryError as err:
            raise SupervisorAppArmorError(
                f"CodeNotary error while processing AppArmor fetch: {err!s}",
                _LOGGER.error,
            ) from err

        # Load
        temp_dir: TemporaryDirectory | None = None

        def write_profile() -> Path:
            nonlocal temp_dir
            temp_dir = TemporaryDirectory(dir=self.sys_config.path_tmp)
            profile_file = Path(temp_dir.name, "apparmor.txt")
            profile_file.write_text(data, encoding="utf-8")
            return profile_file

        try:
            profile_file = await self.sys_run_in_executor(write_profile)

            await self.sys_host.apparmor.load_profile("hassio-supervisor", profile_file)

        except OSError as err:
            if err.errno == errno.EBADMSG:
                self.sys_resolution.add_unhealthy_reason(
                    UnhealthyReason.OSERROR_BAD_MESSAGE
                )
            raise SupervisorAppArmorError(
                f"Can't write temporary profile: {err!s}", _LOGGER.error
            ) from err

        except HostAppArmorError as err:
            raise SupervisorAppArmorError(
                "Can't update AppArmor profile!", _LOGGER.error
            ) from err

        finally:
            if temp_dir:
                await self.sys_run_in_executor(temp_dir.cleanup)

    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update Supervisor version."""
        version = version or self.latest_version

        if version == self.sys_supervisor.version:
            raise SupervisorUpdateError(
                f"Version {version!s} is already installed", _LOGGER.warning
            )

        # First update own AppArmor
        try:
            await self.update_apparmor()
        except SupervisorAppArmorError as err:
            raise SupervisorUpdateError(
                f"Abort update because of an issue with AppArmor: {err!s}",
                _LOGGER.critical,
            ) from err

        # Update container
        _LOGGER.info("Update Supervisor to version %s", version)
        try:
            await self.instance.install(
                version, image=self.sys_updater.image_supervisor
            )
            await self.instance.update_start_tag(
                self.sys_updater.image_supervisor, version
            )
        except DockerError as err:
            self.sys_resolution.create_issue(
                IssueType.UPDATE_FAILED, ContextType.SUPERVISOR
            )
            await async_capture_exception(err)
            raise SupervisorUpdateError(
                f"Update of Supervisor failed: {err!s}", _LOGGER.critical
            ) from err

        self.sys_config.version = version
        self.sys_config.image = self.sys_updater.image_supervisor
        await self.sys_config.save_data()

        self.sys_create_task(self.sys_core.stop())

    @Job(
        name="supervisor_restart",
        conditions=[JobCondition.RUNNING],
        on_condition=SupervisorJobError,
    )
    async def restart(self) -> None:
        """Restart Supervisor soft."""
        self.sys_core.exit_code = 100
        self.sys_create_task(self.sys_core.stop())

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    def logs(self) -> Awaitable[bytes]:
        """Get Supervisor docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    def check_trust(self) -> Awaitable[None]:
        """Calculate Supervisor docker content trust.

        Return Coroutine.
        """
        return self.instance.check_trust()

    async def stats(self) -> DockerStats:
        """Return stats of Supervisor."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise SupervisorError() from err

    async def repair(self):
        """Repair local Supervisor data."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing Supervisor %s", self.version)
        try:
            await self.instance.retag()
        except DockerError:
            _LOGGER.error("Repair of Supervisor failed")

    @Job(
        name="supervisor_check_connectivity",
        limit=JobExecutionLimit.THROTTLE,
        throttle_period=_check_connectivity_throttle_period,
    )
    async def check_connectivity(self):
        """Check the connection."""
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            await self.sys_websession.head(
                "https://checkonline.home-assistant.io/online.txt", timeout=timeout
            )
        except (ClientError, TimeoutError):
            self.connectivity = False
        else:
            self.connectivity = True
