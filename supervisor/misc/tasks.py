"""A collection of tasks."""
import asyncio
from collections.abc import Awaitable
import logging

from ..addons.const import ADDON_UPDATE_CONDITIONS
from ..const import AddonState
from ..coresys import CoreSysAttributes
from ..exceptions import AddonsError, HomeAssistantError, ObserverError
from ..jobs.decorator import Job, JobCondition
from ..plugins.const import PLUGIN_UPDATE_CONDITIONS
from ..utils.sentry import capture_exception

_LOGGER: logging.Logger = logging.getLogger(__name__)

HASS_WATCHDOG_API = "HASS_WATCHDOG_API"

RUN_UPDATE_SUPERVISOR = 29100
RUN_UPDATE_ADDONS = 57600
RUN_UPDATE_CLI = 28100
RUN_UPDATE_DNS = 30100
RUN_UPDATE_AUDIO = 30200
RUN_UPDATE_MULTICAST = 30300
RUN_UPDATE_OBSERVER = 30400

RUN_RELOAD_ADDONS = 10800
RUN_RELOAD_BACKUPS = 72000
RUN_RELOAD_HOST = 7600
RUN_RELOAD_UPDATER = 7200
RUN_RELOAD_INGRESS = 930

RUN_WATCHDOG_HOMEASSISTANT_API = 120

RUN_WATCHDOG_ADDON_APPLICATON = 120
RUN_WATCHDOG_OBSERVER_APPLICATION = 180

RUN_REFRESH_ADDON = 15
RUN_REFRESH_MOUNTS = 900

PLUGIN_AUTO_UPDATE_CONDITIONS = PLUGIN_UPDATE_CONDITIONS + [JobCondition.RUNNING]


class Tasks(CoreSysAttributes):
    """Handle Tasks inside Supervisor."""

    def __init__(self, coresys):
        """Initialize Tasks."""
        self.coresys = coresys
        self._cache = {}

    async def load(self):
        """Add Tasks to scheduler."""
        # Update
        self.sys_scheduler.register_task(self._update_addons, RUN_UPDATE_ADDONS)
        self.sys_scheduler.register_task(self._update_supervisor, RUN_UPDATE_SUPERVISOR)
        self.sys_scheduler.register_task(self._update_cli, RUN_UPDATE_CLI)
        self.sys_scheduler.register_task(self._update_dns, RUN_UPDATE_DNS)
        self.sys_scheduler.register_task(self._update_audio, RUN_UPDATE_AUDIO)
        self.sys_scheduler.register_task(self._update_multicast, RUN_UPDATE_MULTICAST)
        self.sys_scheduler.register_task(self._update_observer, RUN_UPDATE_OBSERVER)

        # Reload
        self.sys_scheduler.register_task(self._reload_store, RUN_RELOAD_ADDONS)
        self.sys_scheduler.register_task(self.sys_updater.reload, RUN_RELOAD_UPDATER)
        self.sys_scheduler.register_task(self.sys_backups.reload, RUN_RELOAD_BACKUPS)
        self.sys_scheduler.register_task(self.sys_host.reload, RUN_RELOAD_HOST)
        self.sys_scheduler.register_task(self.sys_ingress.reload, RUN_RELOAD_INGRESS)
        self.sys_scheduler.register_task(self.sys_mounts.reload, RUN_REFRESH_MOUNTS)

        # Watchdog
        self.sys_scheduler.register_task(
            self._watchdog_homeassistant_api, RUN_WATCHDOG_HOMEASSISTANT_API
        )
        self.sys_scheduler.register_task(
            self._watchdog_observer_application, RUN_WATCHDOG_OBSERVER_APPLICATION
        )
        self.sys_scheduler.register_task(
            self._watchdog_addon_application, RUN_WATCHDOG_ADDON_APPLICATON
        )

        # Refresh
        self.sys_scheduler.register_task(self._refresh_addon, RUN_REFRESH_ADDON)

        _LOGGER.info("All core tasks are scheduled")

    @Job(conditions=ADDON_UPDATE_CONDITIONS + [JobCondition.RUNNING])
    async def _update_addons(self):
        """Check if an update is available for an Add-on and update it."""
        start_tasks: list[Awaitable[None]] = []
        for addon in self.sys_addons.all:
            if not addon.is_installed or not addon.auto_update:
                continue

            # Evaluate available updates
            if not addon.need_update:
                continue
            if not addon.test_update_schema():
                _LOGGER.warning(
                    "Add-on %s will be ignored, schema tests failed", addon.slug
                )
                continue

            # Run Add-on update sequential
            # avoid issue on slow IO
            _LOGGER.info("Add-on auto update process %s", addon.slug)
            try:
                if start_task := await addon.update(backup=True):
                    start_tasks.append(start_task)
            except AddonsError:
                _LOGGER.error("Can't auto update Add-on %s", addon.slug)

        await asyncio.gather(*start_tasks)

    @Job(
        conditions=[
            JobCondition.AUTO_UPDATE,
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.RUNNING,
        ]
    )
    async def _update_supervisor(self):
        """Check and run update of Supervisor Supervisor."""
        if not self.sys_supervisor.need_update:
            return

        _LOGGER.info(
            "Found new Supervisor version %s, updating",
            self.sys_supervisor.latest_version,
        )
        await self.sys_supervisor.update()

    async def _watchdog_homeassistant_api(self):
        """Create scheduler task for monitoring running state of API.

        Try 2 times to call API before we restart Home-Assistant. Maybe we had
        a delay in our system.
        """
        if not self.sys_homeassistant.watchdog:
            # Watchdog is not enabled for Home Assistant
            return
        if self.sys_homeassistant.error_state:
            # Home Assistant is in an error state, this is handled by the rollback feature
            return
        if not await self.sys_homeassistant.core.is_running():
            # The home assistant container is not running
            return
        if self.sys_homeassistant.core.in_progress:
            # Home Assistant has a task in progress
            return
        if await self.sys_homeassistant.api.check_api_state():
            # Home Assistant is running properly
            return

        # Init cache data
        retry_scan = self._cache.get(HASS_WATCHDOG_API, 0)

        # Look like we run into a problem
        retry_scan += 1
        if retry_scan == 1:
            self._cache[HASS_WATCHDOG_API] = retry_scan
            _LOGGER.warning("Watchdog miss API response from Home Assistant")
            return

        _LOGGER.error("Watchdog found a problem with Home Assistant API!")
        try:
            await self.sys_homeassistant.core.restart()
        except HomeAssistantError as err:
            _LOGGER.error("Home Assistant watchdog reanimation failed!")
            capture_exception(err)
        finally:
            self._cache[HASS_WATCHDOG_API] = 0

    @Job(conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_cli(self):
        """Check and run update of cli."""
        if not self.sys_plugins.cli.need_update:
            return

        _LOGGER.info(
            "Found new cli version %s, updating", self.sys_plugins.cli.latest_version
        )
        await self.sys_plugins.cli.update()

    @Job(conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_dns(self):
        """Check and run update of CoreDNS plugin."""
        if not self.sys_plugins.dns.need_update:
            return

        _LOGGER.info(
            "Found new CoreDNS plugin version %s, updating",
            self.sys_plugins.dns.latest_version,
        )
        await self.sys_plugins.dns.update()

    @Job(conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_audio(self):
        """Check and run update of PulseAudio plugin."""
        if not self.sys_plugins.audio.need_update:
            return

        _LOGGER.info(
            "Found new PulseAudio plugin version %s, updating",
            self.sys_plugins.audio.latest_version,
        )
        await self.sys_plugins.audio.update()

    @Job(conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_observer(self):
        """Check and run update of Observer plugin."""
        if not self.sys_plugins.observer.need_update:
            return

        _LOGGER.info(
            "Found new Observer plugin version %s, updating",
            self.sys_plugins.observer.latest_version,
        )
        await self.sys_plugins.observer.update()

    @Job(conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_multicast(self):
        """Check and run update of multicast."""
        if not self.sys_plugins.multicast.need_update:
            return

        _LOGGER.info(
            "Found new Multicast version %s, updating",
            self.sys_plugins.multicast.latest_version,
        )
        await self.sys_plugins.multicast.update()

    async def _watchdog_observer_application(self):
        """Check running state of application and rebuild if they is not response."""
        # if observer plugin is active
        if (
            self.sys_plugins.observer.in_progress
            or await self.sys_plugins.observer.check_system_runtime()
        ):
            return
        _LOGGER.warning("Watchdog/Application found a problem with observer plugin!")

        try:
            await self.sys_plugins.observer.rebuild()
        except ObserverError:
            _LOGGER.error("Observer watchdog reanimation failed!")

    async def _watchdog_addon_application(self):
        """Check running state of the application and start if they is hangs."""
        for addon in self.sys_addons.installed:
            # if watchdog need looking for
            if not addon.watchdog or addon.state != AddonState.STARTED:
                continue

            # Init cache data
            retry_scan = self._cache.get(addon.slug, 0)

            # if Addon have running actions / Application work
            if addon.in_progress or await addon.watchdog_application():
                continue

            # Look like we run into a problem
            retry_scan += 1
            if retry_scan == 1:
                self._cache[addon.slug] = retry_scan
                _LOGGER.warning(
                    "Watchdog missing application response from %s", addon.slug
                )
                return

            _LOGGER.warning("Watchdog found a problem with %s application!", addon.slug)
            try:
                await (await addon.restart())
            except AddonsError as err:
                _LOGGER.error("%s watchdog reanimation failed with %s", addon.slug, err)
                capture_exception(err)
            finally:
                self._cache[addon.slug] = 0

    async def _refresh_addon(self) -> None:
        """Refresh addon state."""
        for addon in self.sys_addons.installed:
            # if watchdog need looking for
            if addon.watchdog or addon.state != AddonState.STARTED:
                continue

            # if Addon have running actions
            if addon.in_progress or await addon.is_running():
                continue

            # Adjust state
            addon.state = AddonState.STOPPED

    @Job(conditions=[JobCondition.SUPERVISOR_UPDATED])
    async def _reload_store(self) -> None:
        """Reload store and check for addon updates."""
        await self.sys_store.reload()
