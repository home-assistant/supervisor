"""A collection of tasks."""

from contextlib import suppress
from datetime import datetime, timedelta
import logging
from typing import cast

from ..apps.const import APP_UPDATE_CONDITIONS
from ..backups.const import LOCATION_CLOUD_BACKUP, LOCATION_TYPE
from ..const import ATTR_TYPE, AppState
from ..coresys import CoreSysAttributes
from ..exceptions import (
    AppsError,
    BackupFileNotFoundError,
    HomeAssistantError,
    HomeAssistantWSError,
    ObserverError,
    SupervisorUpdateError,
)
from ..homeassistant.const import LANDINGPAGE, WSType
from ..jobs.const import JobConcurrency
from ..jobs.decorator import Job, JobCondition
from ..plugins.const import PLUGIN_UPDATE_CONDITIONS
from ..utils.dt import utcnow
from ..utils.sentry import async_capture_exception

_LOGGER: logging.Logger = logging.getLogger(__name__)

HASS_WATCHDOG_API_FAILURES = "HASS_WATCHDOG_API_FAILURES"
HASS_WATCHDOG_REANIMATE_FAILURES = "HASS_WATCHDOG_REANIMATE_FAILURES"
HASS_WATCHDOG_MAX_API_ATTEMPTS = 2
HASS_WATCHDOG_MAX_REANIMATE_ATTEMPTS = 5

RUN_UPDATE_ADDONS = 57600
RUN_UPDATE_CLI = 43200  # 12h, staggered +2min per plugin
RUN_UPDATE_DNS = 43320
RUN_UPDATE_AUDIO = 43440
RUN_UPDATE_MULTICAST = 43560
RUN_UPDATE_OBSERVER = 43680

RUN_RELOAD_ADDONS = 10800
RUN_RELOAD_BACKUPS = 72000
RUN_RELOAD_HOST = 7600
RUN_RELOAD_UPDATER = 86400  # 24h
RUN_RELOAD_INGRESS = 930
RUN_RELOAD_MOUNTS = 900

RUN_WATCHDOG_HOMEASSISTANT_API = 120

RUN_WATCHDOG_ADDON_APPLICATON = 120
RUN_WATCHDOG_OBSERVER_APPLICATION = 180

RUN_CORE_BACKUP_CLEANUP = 86200

PLUGIN_AUTO_UPDATE_CONDITIONS = PLUGIN_UPDATE_CONDITIONS + [
    JobCondition.AUTO_UPDATE,
    JobCondition.RUNNING,
]

OLD_BACKUP_THRESHOLD = timedelta(days=2)


class Tasks(CoreSysAttributes):
    """Handle Tasks inside Supervisor."""

    def __init__(self, coresys):
        """Initialize Tasks."""
        self.coresys = coresys
        self._cache = {}

    async def load(self):
        """Add Tasks to scheduler."""
        # Update
        self.sys_scheduler.register_task(self._update_apps, RUN_UPDATE_ADDONS)
        self.sys_scheduler.register_task(self._update_cli, RUN_UPDATE_CLI)
        self.sys_scheduler.register_task(self._update_dns, RUN_UPDATE_DNS)
        self.sys_scheduler.register_task(self._update_audio, RUN_UPDATE_AUDIO)
        self.sys_scheduler.register_task(self._update_multicast, RUN_UPDATE_MULTICAST)
        self.sys_scheduler.register_task(self._update_observer, RUN_UPDATE_OBSERVER)

        # Reload
        self.sys_scheduler.register_task(self._reload_store, RUN_RELOAD_ADDONS)
        self.sys_scheduler.register_task(self._reload_updater, RUN_RELOAD_UPDATER)
        self.sys_scheduler.register_task(self.sys_backups.reload, RUN_RELOAD_BACKUPS)
        self.sys_scheduler.register_task(self.sys_host.reload, RUN_RELOAD_HOST)
        self.sys_scheduler.register_task(self.sys_ingress.reload, RUN_RELOAD_INGRESS)
        self.sys_scheduler.register_task(self.sys_mounts.reload, RUN_RELOAD_MOUNTS)

        # Watchdog
        self.sys_scheduler.register_task(
            self._watchdog_homeassistant_api, RUN_WATCHDOG_HOMEASSISTANT_API
        )
        self.sys_scheduler.register_task(
            self._watchdog_observer_application, RUN_WATCHDOG_OBSERVER_APPLICATION
        )
        self.sys_scheduler.register_task(
            self._watchdog_app_application, RUN_WATCHDOG_ADDON_APPLICATON
        )

        # Cleanup
        self.sys_scheduler.register_task(
            self._core_backup_cleanup, RUN_CORE_BACKUP_CLEANUP
        )

        _LOGGER.info("All core tasks are scheduled")

    @Job(
        name="tasks_update_addons",
        conditions=APP_UPDATE_CONDITIONS + [JobCondition.RUNNING],
    )
    async def _update_apps(self):
        """Check if an update is available for an App and update it."""
        for app in self.sys_apps.all:
            if not app.is_installed or not app.auto_update:
                continue

            # Evaluate available updates
            if not app.need_update:
                continue
            if not app.auto_update_available:
                _LOGGER.debug(
                    "Not updating app %s from %s to %s as that would cross a known breaking version",
                    app.slug,
                    app.version,
                    app.latest_version,
                )
                continue
            # Delay auto-updates for a day in case of issues
            if utcnow() < app.latest_version_timestamp + timedelta(days=1):
                _LOGGER.debug(
                    "Not updating app %s from %s to %s as the latest version is less than a day old",
                    app.slug,
                    app.version,
                    app.latest_version,
                )
                continue
            if not app.test_update_schema():
                _LOGGER.warning("App %s will be ignored, schema tests failed", app.slug)
                continue

            _LOGGER.info("App auto update process %s", app.slug)
            # Call Home Assistant Core to update app to make sure that backups
            # get created through the Home Assistant Core API (categorized correctly).
            # Ultimately auto updates should be handled by Home Assistant Core itself
            # through a update entity feature.
            message = {
                ATTR_TYPE: WSType.HASSIO_UPDATE_ADDON,
                "addon": app.slug,
                "backup": True,
            }
            _LOGGER.debug(
                "Sending update app WebSocket command to Home Assistant Core: %s",
                message,
            )
            try:
                await self.sys_homeassistant.websocket.async_send_command(message)
            except HomeAssistantWSError as err:
                _LOGGER.warning(
                    "Could not send app update command to Home Assistant Core: %s",
                    err,
                )

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
        if self.sys_homeassistant.version == LANDINGPAGE:
            # Skip watchdog for landingpage
            return
        if not await self.sys_homeassistant.core.is_running():
            # The home assistant container is not running
            return
        if self.sys_homeassistant.core.in_progress:
            # Home Assistant has a task in progress
            return
        if await self.sys_homeassistant.api.check_api_state():
            # Home Assistant is running properly
            self._cache[HASS_WATCHDOG_REANIMATE_FAILURES] = 0
            self._cache[HASS_WATCHDOG_API_FAILURES] = 0
            return

        # Init cache data
        api_fails = self._cache.get(HASS_WATCHDOG_API_FAILURES, 0)

        # Look like we run into a problem
        api_fails += 1
        if api_fails < HASS_WATCHDOG_MAX_API_ATTEMPTS:
            self._cache[HASS_WATCHDOG_API_FAILURES] = api_fails
            _LOGGER.warning("Watchdog missed an Home Assistant Core API response.")
            return

        # After 5 reanimation attempts switch to safe mode. If that fails, give up
        reanimate_fails = self._cache.get(HASS_WATCHDOG_REANIMATE_FAILURES, 0)
        if reanimate_fails > HASS_WATCHDOG_MAX_REANIMATE_ATTEMPTS:
            return

        if safe_mode := reanimate_fails == HASS_WATCHDOG_MAX_REANIMATE_ATTEMPTS:
            _LOGGER.critical(
                "Watchdog cannot reanimate Home Assistant Core, failed all %s attempts. Restarting into safe mode",
                reanimate_fails,
            )
        else:
            _LOGGER.error(
                "Watchdog missed %s Home Assistant Core API responses in a row. Restarting Home Assistant Core!",
                HASS_WATCHDOG_MAX_API_ATTEMPTS,
            )

        try:
            if safe_mode:
                await self.sys_homeassistant.core.rebuild(safe_mode=True)
            else:
                await self.sys_homeassistant.core.restart()
        except HomeAssistantError as err:
            if reanimate_fails == 0 or safe_mode:
                await async_capture_exception(err)

            if safe_mode:
                _LOGGER.critical(
                    "Safe mode restart failed. Watchdog cannot bring Home Assistant online."
                )
            else:
                _LOGGER.error("Home Assistant watchdog reanimation failed!")

            self._cache[HASS_WATCHDOG_REANIMATE_FAILURES] = reanimate_fails + 1
        else:
            self._cache[HASS_WATCHDOG_REANIMATE_FAILURES] = 0
        finally:
            self._cache[HASS_WATCHDOG_API_FAILURES] = 0

    @Job(name="tasks_update_cli", conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_cli(self):
        """Check and run update of cli."""
        if not self.sys_plugins.cli.need_update:
            return

        _LOGGER.info(
            "Found new cli version %s, updating", self.sys_plugins.cli.latest_version
        )
        await self.sys_plugins.cli.update()

    @Job(name="tasks_update_dns", conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_dns(self):
        """Check and run update of CoreDNS plugin."""
        if not self.sys_plugins.dns.need_update:
            return

        _LOGGER.info(
            "Found new CoreDNS plugin version %s, updating",
            self.sys_plugins.dns.latest_version,
        )
        await self.sys_plugins.dns.update()

    @Job(name="tasks_update_audio", conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_audio(self):
        """Check and run update of PulseAudio plugin."""
        if not self.sys_plugins.audio.need_update:
            return

        _LOGGER.info(
            "Found new PulseAudio plugin version %s, updating",
            self.sys_plugins.audio.latest_version,
        )
        await self.sys_plugins.audio.update()

    @Job(name="tasks_update_observer", conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
    async def _update_observer(self):
        """Check and run update of Observer plugin."""
        if not self.sys_plugins.observer.need_update:
            return

        _LOGGER.info(
            "Found new Observer plugin version %s, updating",
            self.sys_plugins.observer.latest_version,
        )
        await self.sys_plugins.observer.update()

    @Job(name="tasks_update_multicast", conditions=PLUGIN_AUTO_UPDATE_CONDITIONS)
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

    async def _watchdog_app_application(self):
        """Check running state of the application and start if they is hangs."""
        for app in self.sys_apps.installed:
            # if watchdog need looking for
            if not app.watchdog or app.state != AppState.STARTED:
                continue

            # Init cache data
            retry_scan = self._cache.get(app.slug, 0)

            # if App have running actions / Application work
            if app.in_progress or await app.watchdog_application():
                continue

            # Look like we run into a problem
            retry_scan += 1
            if retry_scan == 1:
                self._cache[app.slug] = retry_scan
                _LOGGER.warning(
                    "Watchdog missing application response from %s", app.slug
                )
                return

            _LOGGER.warning("Watchdog found a problem with %s application!", app.slug)
            try:
                await (await app.restart())
            except AppsError as err:
                _LOGGER.error("%s watchdog reanimation failed with %s", app.slug, err)
                await async_capture_exception(err)
            finally:
                self._cache[app.slug] = 0

    @Job(
        name="tasks_reload_store",
        conditions=[
            JobCondition.SUPERVISOR_UPDATED,
            JobCondition.OS_SUPPORTED,
            JobCondition.HOME_ASSISTANT_CORE_SUPPORTED,
        ],
    )
    async def _reload_store(self) -> None:
        """Reload store and check for app updates."""
        await self.sys_store.reload()

    @Job(name="tasks_reload_updater")
    async def _reload_updater(self) -> None:
        """Check for new versions of Home Assistant, Supervisor, OS, etc."""
        await self.sys_updater.reload()

        # If there's a new version of supervisor, update immediately
        if self.sys_supervisor.need_update:
            await self._auto_update_supervisor()

    @Job(
        name="tasks_update_supervisor",
        conditions=[
            JobCondition.AUTO_UPDATE,
            JobCondition.FREE_SPACE,
            JobCondition.HEALTHY,
            JobCondition.INTERNET_HOST,
            JobCondition.OS_SUPPORTED,
            JobCondition.RUNNING,
            JobCondition.ARCHITECTURE_SUPPORTED,
        ],
        concurrency=JobConcurrency.REJECT,
    )
    async def _auto_update_supervisor(self):
        """Auto update Supervisor if enabled."""
        if not self.sys_supervisor.need_update:
            return

        _LOGGER.info(
            "Found new Supervisor version %s, updating",
            self.sys_supervisor.latest_version,
        )
        with suppress(SupervisorUpdateError):
            await self.sys_supervisor.update()

    @Job(name="tasks_core_backup_cleanup", conditions=[JobCondition.HEALTHY])
    async def _core_backup_cleanup(self) -> None:
        """Core backup is intended for transient use, remove any old backups that got left behind."""
        old_backups = [
            backup
            for backup in self.sys_backups.list_backups
            if LOCATION_CLOUD_BACKUP in backup.all_locations
            and datetime.fromisoformat(backup.date) < utcnow() - OLD_BACKUP_THRESHOLD
        ]
        for backup in old_backups:
            try:
                await self.sys_backups.remove(
                    backup, [cast(LOCATION_TYPE, LOCATION_CLOUD_BACKUP)]
                )
            except BackupFileNotFoundError as err:
                _LOGGER.debug("Can't remove backup %s: %s", backup.slug, err)
