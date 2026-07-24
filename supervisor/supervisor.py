"""Home Assistant control object."""

import asyncio
from collections.abc import Awaitable
from contextlib import suppress
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
    DockerError,
    HostAppArmorError,
    SupervisorAppArmorError,
    SupervisorJobError,
    SupervisorUnknownError,
    SupervisorUpdateError,
)
from .jobs import ChildJobSyncFilter
from .jobs.const import JobCondition
from .jobs.decorator import Job
from .resolution.const import ContextType, IssueType
from .utils.sentry import async_capture_exception

_LOGGER: logging.Logger = logging.getLogger(__name__)

# Minimum time between two actual connectivity probes. Callers within this
# window get the cached result instead of hitting checkonline.home-assistant.io
# again. The interval shrinks while we're offline so recovery is quick.
_CONNECTIVITY_MIN_INTERVAL_CONNECTED_SEC: float = 600.0
_CONNECTIVITY_MIN_INTERVAL_DISCONNECTED_SEC: float = 5.0


class Supervisor(CoreSysAttributes):
    """Supervisor object."""

    def __init__(self, coresys: CoreSys):
        """Initialize hass object."""
        self.coresys: CoreSys = coresys
        self.instance: DockerSupervisor = DockerSupervisor(coresys)
        self._connectivity: bool = True
        self._connectivity_check: asyncio.Task[None] | None = None
        self._connectivity_rerun_forced: bool = False
        # -inf means "never probed" so the first non-forced call always runs;
        # 0.0 would wrongly short-circuit while loop.time() < min_interval.
        self._connectivity_last_check: float = float("-inf")

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

    def _update_connectivity(self, state: bool) -> None:
        """Update the cached connectivity state and notify listeners if it changed.

        Only :meth:`check_and_update_connectivity` (or the task it spawns)
        should ever call this. Bypass paths that set the state from outside
        an actual probe make it impossible to reason about what the flag
        means.
        """
        if self._connectivity == state:
            return
        _LOGGER.debug(
            "Supervisor connectivity changed: %s -> %s", self._connectivity, state
        )
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
        except AwesomeVersionException, TypeError:
            return False

    @property
    def version(self) -> AwesomeVersion:
        """Return version of running Home Assistant."""
        return AwesomeVersion(SUPERVISOR_VERSION)

    @property
    def latest_version(self) -> AwesomeVersion | None:
        """Return last available version of ."""
        return self.sys_updater.version_supervisor

    @property
    def default_image(self) -> str:
        """Return the default image for this system."""
        return f"ghcr.io/home-assistant/{self.sys_arch.supervisor}-hassio-supervisor"

    @property
    def image(self) -> str | None:
        """Return image name of Supervisor container."""
        return self.instance.image

    @property
    def arch(self) -> str | None:
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
            # Nudge a fresh connectivity check; the probe is authoritative,
            # this error path only hints that something may be wrong.
            self.request_connectivity_check()
            raise SupervisorAppArmorError(
                f"Can't fetch AppArmor profile {url}: {str(err) or 'Timeout'}",
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
            self.sys_resolution.check_oserror(err)
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

    @Job(
        name="supervisor_update",
        # We assume for now the docker image pull is 100% of this task. But from
        # a user perspective that isn't true.  Other steps that take time which
        # is not accounted for in progress include: app armor update and restart
        child_job_syncs=[
            ChildJobSyncFilter("docker_interface_install", progress_allocation=1.0)
        ],
    )
    async def update(self, version: AwesomeVersion | None = None) -> None:
        """Update Supervisor version."""
        version = version or self.latest_version or self.version

        if version == self.version:
            raise SupervisorUpdateError(
                f"Version {version!s} is already installed", _LOGGER.warning
            )

        image = self.sys_updater.image_supervisor or self.instance.image
        if not image:
            raise SupervisorUpdateError(
                "Cannot determine image to use for supervisor update!", _LOGGER.error
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
            await self.instance.install(version, image=image)
            await self.instance.update_start_tag(image, version)
        except DockerError as err:
            self.sys_resolution.create_issue(
                IssueType.UPDATE_FAILED, ContextType.SUPERVISOR
            )
            await async_capture_exception(err)
            raise SupervisorUpdateError(
                f"Update of Supervisor failed: {err!s}", _LOGGER.critical
            ) from err

        self.sys_config.version = version
        self.sys_config.image = image
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
        # Enter STOPPING before the API response is sent, so a request that
        # arrives after it is rejected by the system validation middleware
        # instead of being accepted and then killed when stop() tears down
        # the API server
        await self.sys_core.begin_stop()
        self.sys_create_task(self.sys_core.stop())

    @property
    def in_progress(self) -> bool:
        """Return True if a task is in progress."""
        return self.instance.in_progress

    def logs(self) -> Awaitable[list[str]]:
        """Get Supervisor docker logs.

        Return Coroutine.
        """
        return self.instance.logs()

    async def stats(self) -> DockerStats:
        """Return stats of Supervisor."""
        try:
            return await self.instance.stats()
        except DockerError as err:
            raise SupervisorUnknownError from err

    async def repair(self):
        """Repair local Supervisor data."""
        if await self.instance.exists():
            return

        _LOGGER.info("Repairing Supervisor %s", self.version)
        try:
            await self.instance.retag()
        except DockerError:
            _LOGGER.error("Repair of Supervisor failed")

    def request_connectivity_check(self, *, force: bool = False) -> None:
        """Schedule a connectivity check without awaiting the result.

        Intended for signal handlers (D-Bus, plugin callbacks) that must
        return quickly. Concurrent calls coalesce onto a single in-flight
        check. ``force`` is forwarded to :meth:`check_and_update_connectivity`
        for signals that carry fresh state-change information.
        """
        _LOGGER.debug("Connectivity check requested (force=%s)", force)
        self.sys_create_task(self.check_and_update_connectivity(force=force))

    async def check_and_update_connectivity(self, *, force: bool = False) -> None:
        """Probe Supervisor internet connectivity and update cached state.

        Concurrent callers coalesce onto a single HTTP probe: callers that
        arrive while one is in flight await its completion rather than
        starting a second.

        Without ``force``, a probe that ran within the minimum interval
        short-circuits and the cached state is returned. With ``force``, the
        interval is bypassed and (if a probe is already in flight) a fresh
        one is guaranteed to run once the current probe completes.
        """
        if self._connectivity_check is not None:
            # Probe already in flight - coalesce with it. If the caller
            # needs a fresh result, mark a trailing rerun so the task that
            # owns the in-flight probe runs once more after it completes.
            # Shield so a follower being cancelled cannot bring down the
            # probe that other callers are also waiting on.
            if force:
                _LOGGER.debug(
                    "Connectivity probe in flight; queued forced rerun on completion"
                )
                self._connectivity_rerun_forced = True
            else:
                _LOGGER.debug("Connectivity probe in flight; awaiting its result")
            await asyncio.shield(self._connectivity_check)
            return

        if not force:
            min_interval = (
                _CONNECTIVITY_MIN_INTERVAL_CONNECTED_SEC
                if self._connectivity
                else _CONNECTIVITY_MIN_INTERVAL_DISCONNECTED_SEC
            )
            elapsed = self.sys_loop.time() - self._connectivity_last_check
            if elapsed < min_interval:
                _LOGGER.debug(
                    "Connectivity check within min-interval (%.1fs of %.1fs); "
                    "using cached state %s",
                    elapsed,
                    min_interval,
                    self._connectivity,
                )
                return

        # Awaiting a Task does not propagate cancellation INTO the task, so
        # the owner explicitly cancels the probe on its own cancellation.
        # That keeps the probe from being orphaned (with the next caller
        # starting a second probe alongside the unfinished first).
        probe = self.sys_create_task(self._do_connectivity_check())
        self._connectivity_check = probe
        try:
            await probe
        except asyncio.CancelledError:
            _LOGGER.debug("Connectivity probe owner cancelled; cancelling probe")
            probe.cancel()
            with suppress(asyncio.CancelledError):
                await probe
            raise
        finally:
            if self._connectivity_check is probe:
                self._connectivity_check = None

        # Only count as a recent probe on actual completion. On cancellation
        # the timestamp must stay so the next caller doesn't see a "fresh"
        # cached result that never actually ran.
        self._connectivity_last_check = self.sys_loop.time()

        if self._connectivity_rerun_forced:
            _LOGGER.debug("Running queued forced rerun after probe completion")
            self._connectivity_rerun_forced = False
            await self.check_and_update_connectivity(force=True)

    async def _do_connectivity_check(self) -> None:
        """Run a single HTTP probe and update cached connectivity state."""
        timeout = aiohttp.ClientTimeout(total=10)
        try:
            await self.sys_websession.head(
                "https://checkonline.home-assistant.io/online.txt", timeout=timeout
            )
        except (ClientError, TimeoutError) as err:
            _LOGGER.debug("Supervisor Connectivity check failed: %s", err)
            self._update_connectivity(False)
        else:
            _LOGGER.debug("Supervisor Connectivity check succeeded")
            self._update_connectivity(True)
