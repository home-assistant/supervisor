"""Multible tasks."""
import asyncio
from datetime import datetime
import logging

from .coresys import CoreSysAttributes

_LOGGER = logging.getLogger(__name__)


class Tasks(CoreSysAttributes):
    """Handle Tasks inside HassIO."""

    RUN_UPDATE_SUPERVISOR = 29100
    RUN_UPDATE_ADDONS = 57600

    RUN_RELOAD_ADDONS = 21600
    RUN_RELOAD_SNAPSHOTS = 72000
    RUN_RELOAD_HOST_CONTROL = 72000
    RUN_RELOAD_UPDATER = 21600

    RUN_WATCHDOG_HOMEASSISTANT_DOCKER = 15
    RUN_WATCHDOG_HOMEASSISTANT_API = 300

    RUN_CLEANUP_API_SESSIONS = 900

    def __ini__(self, coresys):
        """Initialize Tasks."""
        self.coresys = coresys
        self._tasks = set()
        self._data = {}

    async def prepare(self):
        """Add Tasks to scheduler."""

        self._tasks.add(self._scheduler.register_task(
            self._update_addons, self.RUN_UPDATE_ADDONS))
        self._tasks.add(self._scheduler.register_task(
            self._update_supervisor, self.RUN_UPDATE_SUPERVISOR))

        self._tasks.add(self._scheduler.register_task(
            self._addons.reload, self.RUN_RELOAD_ADDONS))
        self._tasks.add(self._scheduler.register_task(
            self._updater.reload, self.RUN_RELOAD_UPDATER))

    async def _cleanup_sessions(self):
        """Cleanup old api sessions."""
        now = datetime.now()
        for session, until_valid in self._config.security_sessions.items():
            if now >= until_valid:
                self._config.drop_security_session(session)

    async def _update_addons(self):
        """Check if a update is available of a addon and update it."""
        tasks = []
        for addon in self._addons.list_addons:
            if not addon.is_installed or not addon.auto_update:
                continue

            if addon.version_installed == addon.last_version:
                continue

            if addon.test_udpate_schema():
                tasks.append(addon.update())
            else:
                _LOGGER.warning(
                    "Addon %s will be ignore, schema tests fails", addon.slug)

        if tasks:
            _LOGGER.info("Addon auto update process %d tasks", len(tasks))
            await asyncio.wait(tasks, loop=self._loop)

    async def _update_supervisor(self):
        """Check and run update of supervisor hassio."""
        await self._updater.reload()
        if self._supervisor.last_version == self._supervisor.version:
            return

        # don't perform a update on beta/dev channel
        if self._updater.beta_channel:
            _LOGGER.warning("Ignore Hass.io update on beta upstream!")
            return

        _LOGGER.info("Found new Hass.io version")
        await self._supervisor.update()

    async def _watchdog_homeassistant_docker(self):
        """Check running state of docker and start if they is close."""
        # if Home-Assistant is active
        if not await self._homeassistant.is_initialize() or \
                not self._homeassistant.watchdog:
            return

        # if Home-Assistant is running
        if self._homeassistant.in_progress or \
                await self._homeassistant.is_running():
            return

        _LOGGER.warning("Watchdog found a problem with Home-Assistant docker!")
        await self._homeassistant.run()

    async def _watchdog_homeassistant_api(self):
        """Create scheduler task for montoring running state of API.

        Try 2 times to call API before we restart Home-Assistant. Maybe we had
        a delay in our system.
        """
        retry_scan = self._data.get('HASS_WATCHDOG_API', 0)

        # if Home-Assistant is active
        if not await self._homeassistant.is_initialize() or \
                not self._homeassistant.watchdog:
            return

        # if Home-Assistant API is up
        if self._homeassistant.in_progress or \
                await self._homeassistant.check_api_state():
            return
        retry_scan += 1

        # Retry active
        if retry_scan == 1:
            self._data['HASS_WATCHDOG_API'] = retry_scan
            _LOGGER.warning("Watchdog miss API response from Home-Assistant")
            return

        _LOGGER.error("Watchdog found a problem with Home-Assistant API!")
        await self._homeassistant.restart()
        self._data['HASS_WATCHDOG_API'] = 0
